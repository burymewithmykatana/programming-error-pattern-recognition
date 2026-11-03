"""Fail-closed prototype tests; the optional integration test needs Docker."""
import io
import json
import os

import pytest

from error_pattern_recognition.grading import container_runner as module


class _Input(io.BytesIO):
    def close(self):
        pass


class _Finished:
    def __init__(self, output):
        self.stdin = _Input()
        self.stdout = io.BytesIO(output)
        self.stderr = io.BytesIO(b"")
        self.returncode = 0

    def poll(self):
        return self.returncode


def _runner():
    runner = object.__new__(module.ContainerRunner)
    runner.image_id = "sha256:" + "a" * 64
    runner.worker = "# trusted worker"
    runner.case_timeout = 1.0
    runner.outer_timeout = 10.0
    return runner


def test_expected_output_stays_on_host_and_container_has_no_mounts(monkeypatch):
    captured = {}
    process = _Finished(b'{"status":"ok","actual":7}')
    def fake_popen(args, **kwargs):
        captured["command"] = args
        return process
    monkeypatch.setattr(module.subprocess, "Popen", fake_popen)
    result = _runner().run_case("def f(x): return x", "f", [7], {}, 92830166211)
    assert result == {"status": "failed", "actual": 7}
    assert b"92830166211" not in process.stdin.getvalue()
    assert b"expected" not in process.stdin.getvalue()
    assert "--network=none" in captured["command"] and "--read-only" in captured["command"]
    assert not any(item.startswith(("--mount", "--volume")) for item in captured["command"])


def test_invalid_protocol_fails_closed(monkeypatch):
    monkeypatch.setattr(module.subprocess, "Popen", lambda *a, **kw: _Finished(b"invalid output"))
    assert _runner().run_case("def f(): return 1", "f", [], {}, 1)["status"] == "infrastructure_error"


def test_remote_docker_is_refused_before_execution(monkeypatch):
    monkeypatch.setenv("DOCKER_HOST", "tcp://example.com:2375")
    monkeypatch.setattr(module, "_docker_text", lambda _: pytest.fail("Must not query a remote engine"))
    with pytest.raises(module.SandboxUnavailable, match="remote"):
        module.ContainerRunner()


def test_non_json_inputs_and_invalid_names_rejected():
    runner = _runner()
    with pytest.raises(ValueError, match="JSON-compatible"):
        runner.run_case("def f(x): return x", "f", [(1, 2)], {}, 1)
    with pytest.raises(ValueError, match="identifier"):
        runner.run_case("def f(): return 1", "f(); malicious()", [], {}, 1)


@pytest.mark.skipif(os.environ.get("RUN_CONTAINER_TESTS") != "1", reason="Requires a local Docker engine and python:3.14.3 image")
def test_controlled_container_integration():
    runner = module.ContainerRunner()
    assert runner.run_case("def f(x): return x + 1", "f", [1], {}, 2)["status"] == "passed"
    assert runner.run_case("def f(x): return x - 1", "f", [1], {}, 2)["status"] == "failed"
    assert runner.run_case("def f(x): raise ValueError()", "f", [1], {}, 2)["status"] == "student_error"
    assert runner.run_case("def f(x):\n    while True: pass", "f", [1], {}, 2)["status"] == "timeout"
    restricted = "def f():\n import os, socket\n s=socket.socket()\n s.settimeout(0.2)\n return [os.geteuid(), bool(os.statvfs('/').f_flag & os.ST_RDONLY), s.connect_ex(('192.0.2.1', 9)) != 0]"
    assert runner.run_case(restricted, "f", [], {}, [65534, True, True])["status"] == "passed"
    noisy = "def f():\n import os\n os.write(1, b'not-protocol')\n return 1"
    assert runner.run_case(noisy, "f", [], {}, 1)["status"] == "infrastructure_error"
