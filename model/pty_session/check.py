#!/usr/bin/env python3
"""Bounded model check of the pty_drive session protocol.

Drives the real Protocol class from skills/control-cli/scripts/pty_drive.py
through every emission sequence up to DEPTH events drawn from an alphabet
chosen to stress marker boundaries: banner text containing the DONE marker
before READY, partial markers split across chunks, unrelated noise, quiet
ticks, and early child exit. Every finished session is checked against the
invariants below.

BUGGY_VARIANTS reconstructs the pre-fix code from the git history of
skills/control-cli/SKILL.md. Each variant must produce at least one
invariant violation: the check replays the historical bug and prints its
counterexample trace. A buggy variant that passes means the model no
longer covers that bug — treat it as a failure.

Coverage and rerun instructions: .devin/skills/verify-pty-session/SKILL.md
"""

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DRIVER_SRC = REPO / "skills/control-cli/scripts/pty_drive.py"

spec = importlib.util.spec_from_file_location("pty_drive", DRIVER_SRC)
pty_drive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pty_drive)

Protocol = pty_drive.Protocol

READY = b"READY"
DONE = b"DONE"

CHUNKS = [
    b"banner: DONE is the end marker READY\n",  # DONE text before READY
    READY + b"\n",
    b"REA",
    b"DY\n",
    b"answer ",
    DONE + b"\n",
    b"DO",
    b"NE\n",
    b"noise\n",
]
EVENTS = [("chunk", c) for c in CHUNKS] + [("quiet", None), ("exit", None)]
DEPTH = 5


def run_emission(proto, emission):
    """Replay one event sequence against a Protocol, as run() would."""
    emitted = bytearray()
    trace = []
    for kind, payload in emission:
        if proto.outcome is not None:
            break
        if kind == "chunk":
            emitted += payload
            trace.append(f"chunk {payload!r}")
            action = proto.on_chunk(payload)
            if action == pty_drive.SEND:
                proto.mark_sent()
                trace.append("-> send input")
        elif kind == "quiet":
            trace.append("quiet tick")
            proto.on_quiet()
        else:
            trace.append("child exited")
            proto.on_exit()
    return proto, emitted, trace


def violations(proto, emitted):
    """Invariants checked on every finished session."""
    post = bytes(proto.buffer[proto.sent_offset:]) if proto.sent else b""
    bad = []
    if proto.outcome == pty_drive.DONE and DONE not in post:
        bad.append("DONE outcome without the marker in post-input output")
    if proto.outcome == pty_drive.QUIET:
        if not proto.sent:
            bad.append("QUIET outcome before input was sent")
        elif DONE in post:
            bad.append("QUIET outcome although DONE was already received")
    if bytes(proto.buffer) != bytes(emitted):
        bad.append("transcript does not contain every byte the child emitted")
    return bad


def emissions(depth=DEPTH):
    if depth == 0:
        yield []
        return
    for kind, payload in EVENTS:
        if kind == "exit":
            yield [("exit", None)]
        else:
            for rest in emissions(depth - 1):
                yield [(kind, payload)] + rest


def enumerate_violations(make_proto):
    seen = []
    for emission in emissions():
        proto, emitted, trace = run_emission(make_proto(), emission)
        if proto.outcome is None:
            continue
        bad = violations(proto, emitted)
        if bad:
            seen.append((emission, trace, proto, bad))
    return seen


# --- Historical buggy variants ----------------------------------------------
# Each mirrors the code in skills/control-cli/SKILL.md before the named fix.

class BuggyWholeBufferDone(Protocol):
    """Pre-a71c1eb: the done marker matched the whole buffer, so DONE text
    in a banner ended the session before the reply was sent."""

    def on_chunk(self, data):
        self.buffer += data
        self.quiet_ticks = 0
        if not self.sent:
            return pty_drive.SEND if self.ready_marker in self.buffer else None
        if self.done_marker in bytes(self.buffer):
            return self._finish(pty_drive.DONE)
        return None


class BuggyBreakAfterSend(Protocol):
    """Pre-65cb060: the loop broke immediately after writing the input, so
    the response never reached the transcript."""

    def mark_sent(self):
        super().mark_sent()
        self._finish(pty_drive.DONE)


class BuggyNoDoneCheck(Protocol):
    """Pre-58b872d: quiet was the only end condition, so a session could end
    while the reply — marker and all — sat in the buffer."""

    def on_chunk(self, data):
        self.buffer += data
        self.quiet_ticks = 0
        if not self.sent:
            return pty_drive.SEND if self.ready_marker in self.buffer else None
        return None


class BuggyLostDiagnostics(Protocol):
    """Pre-92f77a1: a child exiting early crashed the read, losing the
    diagnostics it had already printed."""

    def on_exit(self):
        self.buffer.clear()
        return self._finish(pty_drive.CHILD_EXITED)


BUGGY_VARIANTS = {
    "pre-a71c1eb (done marker matched whole buffer)": BuggyWholeBufferDone,
    "pre-65cb060 (broke right after sending input)": BuggyBreakAfterSend,
    "pre-58b872d (quiet was the only end condition)": BuggyNoDoneCheck,
    "pre-92f77a1 (early exit lost diagnostics)": BuggyLostDiagnostics,
}


def make_current():
    return Protocol(READY, DONE, quiet_limit=2)


def main():
    failures = 0

    found = enumerate_violations(make_current)
    if found:
        failures += 1
        emission, trace, proto, bad = found[0]
        print("FAIL: current Protocol violates invariants:")
        for b in bad:
            print(f"  - {b}")
        print("  trace:", " | ".join(trace))
    else:
        print(f"PASS: Protocol holds all invariants over "
              f"{len(EVENTS)} event kinds up to depth {DEPTH}")

    for name, cls in BUGGY_VARIANTS.items():
        found = enumerate_violations(lambda: cls(READY, DONE, quiet_limit=2))
        if not found:
            failures += 1
            print(f"FAIL: {name} produced no violation — the model no "
                  f"longer covers this historical bug")
            continue
        emission, trace, proto, bad = found[0]
        print(f"REPLAYED {name}:")
        for b in bad:
            print(f"  violation: {b}")
        print(f"  trace: {' | '.join(trace)}")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
