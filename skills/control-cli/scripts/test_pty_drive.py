#!/usr/bin/env python3
"""End-to-end tests for pty_drive.py against real child processes.

Each test replays a bug that the old inline PTY snippet in
control-cli/SKILL.md actually shipped (git log skills/control-cli):

- 92f77a1: child exits before READY, diagnostics were lost
- 65cb060: input sent but the response was never read
- 58b872d: a ~1s quiet ended the session, truncating slow replies
- a71c1eb: a DONE-looking string in the banner ended the session early
"""

import shlex
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
DRIVER = HERE / "pty_drive.py"
FAKE = HERE / "fake_cli.py"


def drive(mode, *extra):
    return subprocess.run(
        [
            sys.executable, str(DRIVER),
            "--cmd", shlex.join([sys.executable, str(FAKE), mode]),
            "--ready", "READY" if mode != "repl" else ">>>",
            "--send", "question",
            "--done", "DONE" if mode != "repl" else ">>>",
            "--timeout", "15",
            *extra,
        ],
        capture_output=True,
    )


class PtyDriveTest(unittest.TestCase):
    def test_response_after_input_is_captured(self):
        r = drive("repl")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(b"answer-42", r.stdout)

    def test_done_marker_in_banner_does_not_end_session(self):
        r = drive("banner-done")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(b"real reply DONE", r.stdout)
        self.assertIn(b"outcome=done", r.stderr)

    def test_slow_reply_is_not_truncated_by_quiet(self):
        r = drive("slow-reply")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(b"late answer DONE", r.stdout)
        self.assertIn(b"outcome=done", r.stderr)

    def test_early_exit_preserves_diagnostics(self):
        r = drive("early-exit")
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn(b"FATAL: config file missing", r.stdout)
        self.assertIn(b"outcome=child_exited", r.stderr)

    def test_quiet_fallback_ends_unresponsive_session(self):
        r = drive("deaf", "--quiet-limit", "4")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(b"outcome=quiet", r.stderr)

    def test_deadline_ends_silent_child(self):
        r = subprocess.run(
            [
                sys.executable, str(DRIVER),
                "--cmd", shlex.join([sys.executable, "-c", "import time; time.sleep(30)"]),
                "--ready", "READY", "--send", "x", "--done", "DONE",
                "--timeout", "1",
            ],
            capture_output=True,
        )
        self.assertEqual(r.returncode, 4, r.stderr)
        self.assertIn(b"outcome=timeout", r.stderr)


if __name__ == "__main__":
    unittest.main()
