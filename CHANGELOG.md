# Changelog

Tracks `version` in `.devin-plugin/plugin.json` (`<upstream>-devin.N`).

## 0.15.44-devin.1

- Sync `lib/` and `skills/pstack/{playbooks,references,scripts,agents}` to
  backnotprop/pstack 0.15.44 (`4a4f41c`), up from 0.15.2.
- New skills (11): `benchmark-checklist`, `correct`,
  `create-formal-verification-skill`, `in-your-own-words`, `ketchup`,
  `ketchup-video`, `maintain-formal-verification-skill`, `poteto-help`,
  `principle-explain-the-number`, `sharpen`, `statechart`. No skills removed.
- Removed upstream: the Orchestrate playbook, `scripts/orch`, `scripts/check-plan.mjs`,
  and several leaf `references/` files (folded into their SKILL.md upstream).
- Adapter SKILL.md re-based on the rewritten poteto-mode: condensed triggers
  (first-message goal restatement, worker.md kickoff, benchmark-checklist),
  Explain the Number principle, new model defaults, fresh-subagents rule,
  condensed Writing the reply, Comments section dropped, compact playbook list.
- New Harness mappings: `worker.md` kickoff line via `find` on the child VM,
  named agents (`comment-sicko`) pasted from `agents/<name>.md`, Opus 5.5 /
  Fable 5.2 / Gemini 4 Neon slugs → `devin_mode`, `environment: "local"` →
  `request_local_machine`, `effort`/`generalPurpose` dropped, Claude Code
  settings path, Cursor Project workers and Custom Modes.

## 0.15.2-devin.2

- SKILL.md find-fallback: wait ~15s and retry at session start — plugin files
  materialize at bootstrap and a still-populating cache shows only `.tmp*` dirs.

## 0.15.2-devin.1

- Initial release: adapter SKILL.md + verbatim `lib/` (46 skills) + poteto-mode
  playbooks/references/scripts/agents. lib/ mirrors backnotprop/pstack v0.15.2.
