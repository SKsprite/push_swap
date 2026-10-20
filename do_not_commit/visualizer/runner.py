"""Getting op streams: from the push_swap binary or from a file/stdin."""
import subprocess
import sys
from dataclasses import dataclass, field

from sim import OPS


@dataclass
class RunResult:
    ops: list = field(default_factory=list)
    bench: list = field(default_factory=list)
    error: str = None


def parse_ops(text):
    """Split an op stream; return (ops, error)."""
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    for i, op in enumerate(lines):
        if op not in OPS:
            return [], f"invalid op on line {i + 1}: {op!r}"
    return lines, None


def run_push_swap(binary, strategy, values, timeout=30):
    cmd = [binary, f"--{strategy}", "--bench", *map(str, values)]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout)
    except FileNotFoundError:
        return RunResult(error=f"binary not found: {binary} (run make?)")
    except PermissionError:
        return RunResult(error=f"not executable: {binary}")
    except subprocess.TimeoutExpired:
        return RunResult(error=f"push_swap timed out after {timeout}s")
    bench = [line for line in p.stderr.splitlines() if line.strip()]
    if p.stderr.strip() == "Error":
        return RunResult(bench=bench, error="push_swap printed Error")
    ops, err = parse_ops(p.stdout)
    if not err and p.returncode != 0:
        err = f"push_swap exited with status {p.returncode}"
    return RunResult(ops=ops, bench=bench, error=err)


def read_ops_file(path):
    try:
        text = sys.stdin.read() if path == "-" else open(path).read()
    except OSError as e:
        return RunResult(error=str(e))
    ops, err = parse_ops(text)
    return RunResult(ops=ops, error=err)
