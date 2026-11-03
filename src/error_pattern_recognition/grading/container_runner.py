"""Research-only container runner for a single JSON-compatible function test.

Docker containers share a kernel. This prototype is not a security-reviewed
boundary for hostile submissions and must not be used for classroom deployment.
No host execution fallback is provided.
"""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
import threading
import time
import uuid
from pathlib import Path
from typing import Any

MAX_STREAM = 65536
MAX_PAYLOAD = 131072


class SandboxUnavailable(RuntimeError):
    """The required local Linux container environment is unavailable."""


def _json_value(value: Any, depth: int = 0) -> bool:
    if depth > 20:
        return False
    if value is None or type(value) in (bool, int, str):
        return True
    if type(value) is float:
        return math.isfinite(value)
    if type(value) is list:
        return all(_json_value(item, depth + 1) for item in value)
    if type(value) is dict:
        return all(type(key) is str and _json_value(item, depth + 1) for key, item in value.items())
    return False


def _docker_text(args: list[str]) -> str:
    try:
        result = subprocess.run(["docker", *args], capture_output=True, text=True, timeout=15, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SandboxUnavailable("Docker is unavailable or did not respond.") from exc
    if result.returncode:
        raise SandboxUnavailable("Docker could not provide the required local Linux environment.")
    return result.stdout.strip()


class ContainerRunner:
    """Prototype runner with network disabled, no mounts and bounded resources."""

    def __init__(self, image: str = "python:3.14.3", *, case_timeout: float = 2.0,
                 outer_timeout: float = 20.0) -> None:
        if not re.fullmatch(r"[A-Za-z0-9_./:@-]+", image) or image.startswith("-"):
            raise ValueError("Invalid image name.")
        if not (0 < case_timeout <= 10 and case_timeout < outer_timeout <= 60):
            raise ValueError("Invalid runner timeouts.")
        endpoint_override = os.environ.get("DOCKER_HOST", "")
        if endpoint_override and not endpoint_override.startswith(("npipe://", "unix://")):
            raise SandboxUnavailable("A remote Docker endpoint is not allowed.")
        endpoint = _docker_text(["context", "inspect", "--format", "{{.Endpoints.docker.Host}}"])
        if not endpoint.startswith(("npipe://", "unix://")):
            raise SandboxUnavailable("A local Docker endpoint is required.")
        if _docker_text(["info", "--format", "{{.OSType}}"]) != "linux":
            raise SandboxUnavailable("A Linux Docker engine is required.")
        image_id = _docker_text(["image", "inspect", "--format", "{{.Id}}", image])
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", image_id):
            raise SandboxUnavailable("The local image could not be identified by its immutable ID.")
        self.image_id = image_id
        self.case_timeout = case_timeout
        self.outer_timeout = outer_timeout
        self.worker = Path(__file__).with_name("_container_worker.py").read_text(encoding="utf-8")

    def run_case(self, code: str, function_name: str, args: list[Any], kwargs: dict[str, Any], expected: Any) -> dict[str, Any]:
        """Execute a single case. Expected output is compared only on the host."""
        if not isinstance(code, str) or not code.strip() or len(code.encode("utf-8")) > 65536:
            raise ValueError("Submission must be nonempty text up to 64 KiB.")
        if not isinstance(function_name, str) or not function_name.isidentifier():
            raise ValueError("Function name must be a Python identifier.")
        if type(args) is not list or type(kwargs) is not dict or not _json_value(args) or not _json_value(kwargs) or not _json_value(expected):
            raise ValueError("Inputs and expected output must be JSON-compatible values.")
        payload = json.dumps({"code": code, "function_name": function_name, "args": args, "kwargs": kwargs,
                              "case_timeout_seconds": self.case_timeout}, ensure_ascii=False, allow_nan=False).encode("utf-8")
        if len(payload) > MAX_PAYLOAD:
            raise ValueError("Execution payload is too large.")
        name = f"grading-research-{uuid.uuid4().hex}"
        cmd = ["docker", "run", "--rm", "--pull=never", "--name", name, "--network=none", "--read-only",
               "--memory=96m", "--memory-swap=96m", "--cpus=0.5", "--pids-limit=32", "--cap-drop=ALL",
               "--security-opt=no-new-privileges", "--user=65534:65534", "--tmpfs=/tmp:rw,noexec,nosuid,nodev,size=8m",
               "--entrypoint=python", "-i", self.image_id, "-I", "-c", self.worker]
        try:
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError:
            return {"status": "infrastructure_error", "reason": "Could not start Docker client."}
        streams = {"stdout": bytearray(), "stderr": bytearray()}
        exceeded = threading.Event()

        def read_stream(pipe, destination):
            try:
                while True:
                    chunk = pipe.read(4096)
                    if not chunk:
                        break
                    remaining = MAX_STREAM - len(destination)
                    destination.extend(chunk[:max(remaining, 0)])
                    if len(chunk) > remaining:
                        exceeded.set()
            except (OSError, ValueError):
                exceeded.set()

        def write_input():
            try:
                process.stdin.write(payload)
                process.stdin.close()
            except (BrokenPipeError, OSError, ValueError):
                pass

        threads = [threading.Thread(target=read_stream, args=(process.stdout, streams["stdout"]), daemon=True),
                   threading.Thread(target=read_stream, args=(process.stderr, streams["stderr"]), daemon=True),
                   threading.Thread(target=write_input, daemon=True)]
        for thread in threads:
            thread.start()
        deadline = time.monotonic() + self.outer_timeout
        while process.poll() is None and time.monotonic() < deadline and not exceeded.is_set():
            time.sleep(0.05)
        aborted = process.poll() is None
        if aborted:
            process.kill()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
        if aborted or process.returncode != 0:
            try:
                cleanup = subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=10, check=False)
                cleanup_confirmed = cleanup.returncode == 0 or b"No such container" in cleanup.stderr
            except (OSError, subprocess.TimeoutExpired):
                cleanup_confirmed = False
        else:
            cleanup_confirmed = True  # --rm removed the stopped container.
        for thread in threads:
            thread.join(timeout=2)
        if aborted or exceeded.is_set() or any(thread.is_alive() for thread in threads):
            return {"status": "infrastructure_error", "reason": "Container timed out or exceeded the output limit.",
                    "cleanup_confirmed": cleanup_confirmed, "container_name": name if not cleanup_confirmed else None}
        if process.returncode != 0:
            return {"status": "infrastructure_error", "reason": "Container failed before returning a result.",
                    "cleanup_confirmed": cleanup_confirmed, "container_name": name if not cleanup_confirmed else None}
        try:
            response = json.loads(streams["stdout"].decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {"status": "infrastructure_error", "reason": "Container returned an invalid result."}
        if not isinstance(response, dict):
            return {"status": "infrastructure_error", "reason": "Container returned an invalid result."}
        status = response.get("status")
        if status == "ok" and "actual" in response and _json_value(response["actual"]):
            return {"status": "passed" if response["actual"] == expected else "failed", "actual": response["actual"]}
        if status in ("student_error", "timeout"):
            return {"status": status, "error_type": str(response.get("error_type", ""))[:100]}
        return {"status": "infrastructure_error", "reason": "Unsupported or malformed output."}
