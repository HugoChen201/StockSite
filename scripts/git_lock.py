#!/usr/bin/env python3
"""Shared non-overlap lock for StockSite data.json writers.

Every process that does `git pull -> patch data.json -> git commit -> git push`
must hold this lock for the whole sequence, so the five-minute updater, the
morning/close scans, and the MomoEdge Flow & Pulse job can never interleave
their read-modify-write cycles and clobber each other's patches.

Python use:
    from git_lock import locked
    with locked():
        ... pull, patch, commit, push ...

Shell use (cron bodies, including subprocesses that call update-data.py):
    python3 scripts/git_lock.py -- bash -c 'git pull --ff-only; python3 scripts/update-data.py /tmp/patch.json; ...'

The lock is reentrant within one process (a counter) and the CLI wrapper sets
STOCKSITE_DATA_LOCK=1 for its children so update-data.py does not deadlock
trying to re-acquire a lock its own wrapper already holds.
"""
import fcntl
import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
LOCK_FILE = REPO / ".git" / "stocksite-data.lock"
_ENV_FLAG = "STOCKSITE_DATA_LOCK"

_depth = 0
_fd = None


@contextmanager
def locked(timeout=None):
    """Hold the shared data-update lock (reentrant in this process).

    timeout=None blocks until the lock is free (default). With a timeout in
    seconds, makes non-blocking attempts until the deadline, then raises
    TimeoutError so a frequent lightweight writer can skip its slot instead
    of piling up behind a long extraction.
    """
    global _depth, _fd
    if _depth > 0 or os.environ.get(_ENV_FLAG) == "1":
        yield
        return
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    _fd = open(LOCK_FILE, "w")
    if timeout is None:
        fcntl.flock(_fd, fcntl.LOCK_EX)  # blocks until the other writer finishes
    else:
        import time
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    _fd.close()
                    _fd = None
                    raise TimeoutError("stocksite data lock busy")
                time.sleep(2)
    _depth += 1
    try:
        yield
    finally:
        _depth -= 1
        fcntl.flock(_fd, fcntl.LOCK_UN)
        _fd.close()
        _fd = None


def main():
    if len(sys.argv) < 3 or sys.argv[1] != "--":
        print("usage: git_lock.py -- <command> [args...]", file=sys.stderr)
        sys.exit(2)
    with locked():
        env = dict(os.environ)
        env[_ENV_FLAG] = "1"
        r = subprocess.run(sys.argv[2:], cwd=str(REPO), env=env)
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
