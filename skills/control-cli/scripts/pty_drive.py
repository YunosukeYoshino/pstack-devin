#!/usr/bin/env python3
"""Drive an interactive CLI over a PTY and capture its transcript.

Usage:
    python3 pty_drive.py --cmd <command...> --ready <text> \
        --send <line> --done <text> [--timeout SECS] [--quiet-limit TICKS]

Protocol: wait for READY in the child's output, write SEND + newline to
the PTY, then keep reading until DONE appears in the bytes the child
emitted *after* the input was sent. DONE text that arrived before the
input (banner, an earlier prompt) does not end the session. Silence ends
it only as a fallback once input was sent. A child that exits early
still yields everything it printed.

Exit codes: 0 = done marker or quiet fallback, 3 = child exited first,
4 = wall-clock timeout, 2 = usage error.
"""

import argparse
import os
import pty
import select
import shlex
import subprocess
import sys
import time

TICK_SECONDS = 0.25

SEND = "send"
DONE = "done"
QUIET = "quiet"
CHILD_EXITED = "child_exited"
TIMEOUT = "timeout"

EXIT_CODE = {DONE: 0, QUIET: 0, CHILD_EXITED: 3, TIMEOUT: 4}


class Protocol:
    """One PTY session as a pure state machine over input events.

    run() feeds it on_chunk/on_quiet/on_exit; it returns SEND or a
    finish outcome and never does I/O, so model checkers and tests can
    drive the same transitions without a terminal.
    """

    def __init__(self, ready_marker: bytes, done_marker: bytes, quiet_limit: int):
        self.ready_marker = ready_marker
        self.done_marker = done_marker
        self.quiet_limit = quiet_limit
        self.buffer = bytearray()
        self.sent_offset: int | None = None
        self.quiet_ticks = 0
        self.outcome: str | None = None

    @property
    def sent(self) -> bool:
        return self.sent_offset is not None

    def post_input(self) -> bytes:
        return bytes(self.buffer[self.sent_offset:])

    def on_chunk(self, data: bytes) -> str | None:
        self.buffer += data
        self.quiet_ticks = 0
        if not self.sent:
            return SEND if self.ready_marker in self.buffer else None
        if self.done_marker in self.post_input():
            return self._finish(DONE)
        return None

    def mark_sent(self) -> None:
        self.sent_offset = len(self.buffer)

    def on_quiet(self) -> str | None:
        if self.sent:
            self.quiet_ticks += 1
            if self.quiet_ticks >= self.quiet_limit:
                return self._finish(QUIET)
        return None

    def on_exit(self) -> str:
        return self._finish(CHILD_EXITED)

    def on_timeout(self) -> str:
        return self._finish(TIMEOUT)

    def _finish(self, outcome: str) -> str:
        if self.outcome is None:
            self.outcome = outcome
        return self.outcome


def parse_args(argv):
    p = argparse.ArgumentParser(
        prog="pty_drive.py",
        description="Drive an interactive CLI over a PTY and capture its transcript.",
    )
    p.add_argument("--cmd", required=True,
                   help="command under test, as one shell-style string")
    p.add_argument("--ready", required=True,
                   help="text meaning the CLI is ready for input")
    p.add_argument("--send", required=True,
                   help="input written once READY appears; a newline is appended")
    p.add_argument("--done", required=True,
                   help="text ending the session, matched only in post-input output")
    p.add_argument("--timeout", type=float, default=30.0,
                   help="wall-clock cap in seconds (default 30)")
    p.add_argument("--quiet-limit", type=int, default=20,
                   help="silent %.2fs ticks allowed after send (default 20)"
                   % TICK_SECONDS)
    return p.parse_args(argv)


def run(args) -> Protocol:
    proto = Protocol(
        args.ready.encode(), args.done.encode(), args.quiet_limit
    )
    master_fd, slave_fd = pty.openpty()
    proc = subprocess.Popen(
        shlex.split(args.cmd),
        stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
        close_fds=True,
    )
    os.close(slave_fd)
    deadline = time.monotonic() + args.timeout
    try:
        while proto.outcome is None:
            if time.monotonic() >= deadline:
                proto.on_timeout()
                break
            ready, _, _ = select.select([master_fd], [], [], TICK_SECONDS)
            if not ready:
                if proc.poll() is not None:
                    proto.on_exit()
                    break
                proto.on_quiet()
                continue
            try:
                chunk = os.read(master_fd, 4096)
            except OSError:
                proto.on_exit()
                break
            if not chunk:
                proto.on_exit()
                break
            if proto.on_chunk(chunk) == SEND:
                os.write(master_fd, args.send.encode() + b"\n")
                proto.mark_sent()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        os.close(master_fd)
    return proto


def main(argv=None) -> int:
    args = parse_args(argv)
    proto = run(args)
    sys.stdout.buffer.write(bytes(proto.buffer))
    sys.stdout.flush()
    sys.stderr.write(f"pty-drive: outcome={proto.outcome} sent={proto.sent}\n")
    return EXIT_CODE.get(proto.outcome, 4)


if __name__ == "__main__":
    sys.exit(main())
