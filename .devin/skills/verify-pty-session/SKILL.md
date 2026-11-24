---
name: verify-pty-session
description: "Re-run the bounded model check of the control-cli PTY session protocol whenever skills/control-cli/scripts/pty_drive.py or its Protocol class changes. Use when touching the ready/send/done/quiet/exit logic, adding an outcome, or before merging a sync that carries upstream control-cli edits."
---

# Verify the PTY session protocol

`model/pty_session/check.py` exhaustively drives the real `Protocol` class
from `skills/control-cli/scripts/pty_drive.py` through every emission
sequence up to depth 5 drawn from an 11-event alphabet (banner text with a
premature DONE marker, split markers, noise, quiet ticks, early exit) and
checks three invariants on every finished session:

- DONE outcome ⇒ the done marker occurs in post-input output.
- QUIET outcome ⇒ input was sent and the done marker is not already
  sitting in post-input output.
- The transcript contains every byte the child emitted.

It then replays four historical bugs (see `BUGGY_VARIANTS`, each tagged
with the pre-fix commit it mirrors) and requires each to violate an
invariant. The REPLAYED traces are the past bugs caught in the act.

## Run

```bash
python3 model/pty_session/check.py
```

Exit 0 = protocol holds over the whole bounded space AND every buggy
variant reproduced its violation. ~3s, python3 stdlib only. CI runs it in
`.github/workflows/model-check.yml`.

## Reading failures

- `FAIL: current Protocol violates invariants` — the real code broke a
  property. The printed trace is the shortest emission that breaks it;
  replay it against `pty_drive.py` directly to confirm.
- `FAIL: <variant> produced no violation` — the model drifted from the
  bug it replays (event alphabet shrank, depth dropped, or the invariant
  was weakened). Fix the model, not the variant.
- An import error for `pty_drive.py` — the checked file moved; update
  `DRIVER_SRC` at the top of `check.py`.

## Coverage and sync

Covers `Protocol` (`on_chunk`, `mark_sent`, `on_quiet`, `on_exit`,
`on_timeout`) in `skills/control-cli/scripts/pty_drive.py` as of commit
`3f31023` (the commit that introduced the file; content-identical on
`main` after PR #6 merged). After any change to that file, run the check;
if it still passes and the transitions still match the code, update the
sync commit recorded here. If it fails, fix the code or, for an intended
protocol change, update `BUGGY_VARIANTS`/invariants deliberately — never
weaken them to force a pass.

Not covered: real `select()`/PTY timing, process lifecycle and exit
codes, PTY echo content, and quiet limits other than 2 ticks. Those are
I/O-shell concerns in `run()`/`main()`, covered by the e2e tests in
`skills/control-cli/scripts/test_pty_drive.py`.

## When the protocol changes on purpose

Add the new transition to `Protocol`, mirror any new historical bug in
`BUGGY_VARIANTS`, rerun, and move the sync commit forward in this file.
Use `/maintain-formal-verification-skill` for a deeper re-derivation.
