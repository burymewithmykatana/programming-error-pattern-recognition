"""Container-side protocol for one function call. Not a standalone sandbox."""
from __future__ import annotations

import contextlib
import json
import math
import signal
import sys

MAX_OUTPUT = 32768


class _Timeout(BaseException):
    pass


class _CappedText:
    def __init__(self) -> None:
        self.size = 0

    def write(self, text: str) -> int:
        self.size += len(text.encode("utf-8", errors="replace"))
        if self.size > MAX_OUTPUT:
            raise RuntimeError("Output limit exceeded")
        return len(text)

    def flush(self) -> None:
        pass


def _json_value(value, depth=0):
    if depth > 20:
        raise ValueError("Output nesting too deep")
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is float and math.isfinite(value):
        return value
    if type(value) is list:
        return [_json_value(item, depth + 1) for item in value]
    if type(value) is dict and all(type(key) is str for key in value):
        return {key: _json_value(item, depth + 1) for key, item in value.items()}
    raise ValueError("Output is not a supported JSON value")


def _alarm(_signal, _frame):
    raise _Timeout()


def main():
    payload = json.loads(sys.stdin.buffer.read(131073))
    code, entry = payload["code"], payload["function_name"]
    output = _CappedText()
    signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, payload["case_timeout_seconds"])
    try:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            namespace = {"__name__": "__student__"}
            exec(compile(code, "<submission>", "exec"), namespace)
            function = namespace.get(entry)
            if not callable(function):
                raise ValueError("Required function is missing or not callable")
            result = function(*payload["args"], **payload["kwargs"])
            try:
                value = _json_value(result)
                encoded = json.dumps({"status": "ok", "actual": value}, allow_nan=False, separators=(",", ":"))
                if len(encoded.encode("utf-8")) > MAX_OUTPUT:
                    raise ValueError("Result is too large")
                response = encoded
            except (ValueError, TypeError, OverflowError, RecursionError):
                response = '{"status":"unsupported_output"}'
    except _Timeout:
        response = '{"status":"timeout"}'
    except BaseException as exc:
        response = json.dumps({"status": "student_error", "error_type": type(exc).__name__})
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    print(response, flush=True)


if __name__ == "__main__":
    main()
