#!/usr/bin/env python3
"""Fake interactive CLIs for test_pty_drive.py. Each mode reproduces a
child behavior that broke a past version of the PTY harness protocol."""

import sys
import time

mode = sys.argv[1]

if mode == "repl":
    print(">>>", flush=True)
    sys.stdin.readline()
    print("answer-42")
    print(">>>", flush=True)
    time.sleep(30)

elif mode == "banner-done":
    # The done text sits in the banner, before input (commit a71c1eb).
    print("shell READY - the prompt DONE marks a finished reply")
    sys.stdout.flush()
    sys.stdin.readline()
    print("real reply DONE", flush=True)
    time.sleep(30)

elif mode == "slow-reply":
    # Reply lands after ~1.2s of silence; the pre-58b872d harness ended
    # the session at ~1s of quiet and truncated it.
    print("READY", flush=True)
    sys.stdin.readline()
    time.sleep(1.2)
    print("late answer DONE", flush=True)
    time.sleep(30)

elif mode == "early-exit":
    # Dies before READY; the pre-92f77a1 harness lost this diagnostic.
    print("FATAL: config file missing")
    sys.exit(1)

elif mode == "deaf":
    # Prints READY but never replies; only the quiet fallback ends it.
    print("READY", flush=True)
    sys.stdin.readline()
    time.sleep(30)

sys.exit(0)
