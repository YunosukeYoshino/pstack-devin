# Changelog

Tracks `version` in `.devin-plugin/plugin.json` (`<upstream>-devin.N`).

## 0.15.48-devin.1

- Sync `skills/` and `skills/pstack/agents` to backnotprop/pstack 0.15.48
  (`c81f1bf`), up from 0.15.46.
- New skill `reframe` (expert vocabulary for what you're building, with
  checked citations, then a rewritten description). Listed in README.
  poteto-help now routes to it. No removed skills.
- poteto-mode `SKILL.md` is unchanged, so the adapter needed no edits.

## 0.15.46-devin.1

- Sync `skills/` and `skills/pstack/agents` to backnotprop/pstack 0.15.46
  (`d164eec`), up from 0.15.44. No new or removed skills.
- Upstream raised the Gemini panel seat from `gemini-4-neon-high` to
  `gemini-4-neon-xhigh` (poteto-mode, arena, setup-pstack). The adapter's
  model-name mapping and panel line now name `gemini-4-neon-xhigh`.
- Upstream added `agents/openai.yaml` (Codex invocation policy) to each
  skill. Mirrored verbatim; Devin ignores it.
- statechart: POSIX launcher note for native Windows; watch-pr script fixes.

## 0.15.44-devin.2

- Restructure: `lib/` moved to `skills/` so every leaf skill is directly
  invocable as `/<plugin>:<name>` (same UX as pstack-ports/devin-pstack).
  The adapter still routes internal skill calls as file reads, so the
  one-active-skill constraint is unchanged.
- `skills/pstack/{playbooks,references,scripts}` removed — they were
  byte-identical copies of `skills/poteto-mode/`'s own extras, which now
  hold the canonical copies.
- New bundled skills from `cursor-team-kit` (via pstack-ports/devin-pstack):
  `deslop`, `control-cli`, `control-ui`. The adapter's Harness section now
  points at them instead of saying they are missing.
- `sync-upstream.sh` syncs upstream `skills/` into `skills/` directly
  (excluding `pstack/` and the three cursor-team-kit ports) and drops the
  duplicated poteto-mode extras pass.

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
