# pstack-devin

[poteto-mode](https://github.com/backnotprop/pstack) (pstack) as a Devin Cloud plugin — the full skill library, with every leaf skill invocable as `/<plugin>:<name>` and an adapter that routes poteto-mode's internal skill calls as file reads for Devin's one-active-skill model.

## Why this exists

Devin keeps exactly **one skill active** at a time: invoking another skill replaces the active one ([Devin docs](https://docs.devin.ai/product-guides/skills)). pstack's design is the opposite — `poteto-mode` routes internally to `how`, `architect`, `swarm`, `tdd`, `interrogate`, and ~40 sibling skills, expecting each to become active on demand.

`pstack-devin` resolves that mismatch with a structural adapter:

- **`skills/pstack/SKILL.md`** — the adapter skill (`@skills:pstack` / `/pstack-devin:pstack`). It contains poteto-mode's philosophy verbatim (non-negotiables, principles, autonomy, writing rules, playbook index) plus a Devin adapter-rules section that replaces skill-invocation with file reads, and Devin-native mappings for subagents, questions, and review. `skills/pstack/agents/` holds the named-agent briefs (`poteto-agent`, `comment-sicko`).
- **`skills/<name>/`** — the complete pstack skill library (verbatim from upstream), including `poteto-mode` with its 22 playbooks, `references/`, `scripts/`, and `worker.md`. Each leaf is directly invocable (`/pstack-devin:unslop`, `/pstack-devin:how`, …) — matching [pstack-ports/devin-pstack](https://github.com/pstack-ports/devin-pstack)'s UX — and when the adapter routes to "the `how` skill" the session reads `skills/how/SKILL.md` as a file instead of invoking a skill, so routing never disturbs the active skill.
- **`skills/{deslop,control-cli,control-ui}`** — the `cursor-team-kit` skills pstack playbooks call, ported from [pstack-ports/devin-pstack](https://github.com/pstack-ports/devin-pstack) (not part of upstream pstack; synced by hand).

Because the library is bundled as real files inside the plugin, installed plugins materialize under `~/.devin/plugins/cache/` (per session — a fresh session after install is what materializes them) and every reference resolves on disk. If the find anchor in the skill comes back empty on an older session, start a fresh session; the adapter says so itself when it happens.

## Install

In Devin: **Settings → Plugins → Install from URL** and paste this repo's URL:

```
https://github.com/YunosukeYoshino/pstack-devin
```

Then in any session:

```
@skills:pstack <your task>
```

Any leaf skill can also be invoked directly, e.g. `/pstack-devin:unslop` or `/pstack-devin:tdd`. Upstream marks them `disable-model-invocation`, so they only fire when named.

For organization-wide install, install the repo URL under your org's plugin settings. Avoid also installing an uploaded copy — two installs register duplicate `pstack` skills, and uploads diverge from this repo's versioning.

## Usage

Start non-trivial tasks with the adapter:

```
@skills:pstack this pr has a subtle bug where the scroll drifts every 750ms even when idle. repro first, then fix and verify.
```

It reads the task, matches it to one of the 22 playbooks in [`skills/poteto-mode/playbooks/`](./skills/poteto-mode/playbooks/), and routes to leaf skills as the steps fire.

Reach for a leaf directly when you want just that skill:

```
/pstack-devin:how do we cancel runs? do we have an n+1 when we look up every run to cancel?
```

```
/pstack-devin:interrogate review this pr.
```

Prefer `/pstack-devin:pstack` (the adapter) over `/pstack-devin:poteto-mode`: the raw leaf is upstream-verbatim, so its harness section maps delegation to local subagents, not Devin child sessions. Only the adapter carries the Devin mappings.

<details>
<summary>all skills</summary>

| skill | use it when |
|---|---|
| [`/pstack-devin:pstack`](./skills/pstack/SKILL.md) | default entry point: poteto-mode plus the Devin adapter mappings. |
| [`/pstack-devin:poteto-mode`](./skills/poteto-mode/SKILL.md) | the raw upstream leaf; prefer `pstack` so delegation uses Devin child sessions. |
| [`/pstack-devin:poteto-help`](./skills/poteto-help/SKILL.md) | you're new to pstack or unsure which skill, playbook, or principle fits. |
| [`/pstack-devin:in-your-own-words`](./skills/in-your-own-words/SKILL.md) | you want the agent to play back your goal before it starts. |
| [`/pstack-devin:sharpen`](./skills/sharpen/SKILL.md) | you want a prompt made deeper, not bigger, before you send it. |
| [`/pstack-devin:how`](./skills/how/SKILL.md) | you want a walkthrough of how a subsystem works. |
| [`/pstack-devin:why`](./skills/why/SKILL.md) | you want to know why something was built this way, with cited evidence. |
| [`/pstack-devin:recall`](./skills/recall/SKILL.md) | you want your recent context on a topic rebuilt as a tight current-state brief. |
| [`/pstack-devin:ketchup`](./skills/ketchup/SKILL.md) | you want what changed since your last message, with every item waiting on you listed. |
| [`/pstack-devin:ketchup-video`](./skills/ketchup-video/SKILL.md) | you want the catch-up as a short subtitled slide video. |
| [`/pstack-devin:blast-radius`](./skills/blast-radius/SKILL.md) | you have a small-looking change and want to know what else it could break. |
| [`/pstack-devin:architect`](./skills/architect/SKILL.md) | you're about to write code and want types and module shape settled first. |
| [`/pstack-devin:arena`](./skills/arena/SKILL.md) | you want N parallel attempts, then the best parts of each grafted into one. |
| [`/pstack-devin:swarm`](./skills/swarm/SKILL.md) | you want N parallel workers on different slices, then one aggregated report. |
| [`/pstack-devin:interrogate`](./skills/interrogate/SKILL.md) | you want different models to try to break a diff, keeping only proven findings. |
| [`/pstack-devin:automate-me`](./skills/automate-me/SKILL.md) | you want your own `-mode` skill drafted from how you actually work. |
| [`/pstack-devin:make-bot-ui`](./skills/make-bot-ui/SKILL.md) | you want a page whose buttons wake an agent. Upstream-verbatim and Cursor-flavored — the adapter maps it to a `webhook:incoming` Devin Automation. |
| [`/pstack-devin:setup-pstack`](./skills/setup-pstack/SKILL.md) | you want to pick which models pstack uses per role. |
| [`/pstack-devin:reflect`](./skills/reflect/SKILL.md) | a long task landed and you want the recipe captured as a skill edit. |
| [`/pstack-devin:correct`](./skills/correct/SKILL.md) | you keep correcting agents for the same mistakes; fixes each at the highest level that works. |
| [`/pstack-devin:teach`](./skills/teach/SKILL.md) | you want to actually understand a change, built up diagram by diagram. |
| [`/pstack-devin:tdd`](./skills/tdd/SKILL.md) | there's a cheap local test path: failing test first, then the fix. |
| [`/pstack-devin:benchmark-checklist`](./skills/benchmark-checklist/SKILL.md) | you measured a speedup or regression and want the number vetted before acting on it. |
| [`/pstack-devin:no-comments`](./skills/no-comments/SKILL.md) | strip comments before review via Comment Sicko. |
| [`/pstack-devin:typescript-best-practices`](./skills/typescript-best-practices/SKILL.md) | you're reading or editing TypeScript. |
| [`/pstack-devin:figure-it-out`](./skills/figure-it-out/SKILL.md) | no playbook fits; designs a rigorous, auditable playbook for the task. |
| [`/pstack-devin:show-me-your-work`](./skills/show-me-your-work/SKILL.md) | you want a reviewable decision trail logged to a TSV. |
| [`/pstack-devin:create-verification-skill`](./skills/create-verification-skill/SKILL.md) | your project has no scripted way to prove app behavior. |
| [`/pstack-devin:maintain-verification-skill`](./skills/maintain-verification-skill/SKILL.md) | your verify skill's feature map has drifted from the app. |
| [`/pstack-devin:create-formal-verification-skill`](./skills/create-formal-verification-skill/SKILL.md) | tests can't reach the case that breaks a race, state machine, or parser. |
| [`/pstack-devin:maintain-formal-verification-skill`](./skills/maintain-formal-verification-skill/SKILL.md) | code your formal verification covers has changed since last checked. |
| [`/pstack-devin:statechart`](./skills/statechart/SKILL.md) | someone who owns the behavior needs to see it drawn, not read a spec. |
| [`/pstack-devin:unslop`](./skills/unslop/SKILL.md) | you're cleaning up writing; removes AI tells. |
| [`/pstack-devin:deslop`](./skills/deslop/SKILL.md) | you want AI slop swept out of the diff before commit. |
| [`/pstack-devin:bro`](./skills/bro/SKILL.md) | you want the last message restated in plain human language. |
| [`/pstack-devin:technical-writing`](./skills/technical-writing/SKILL.md) | docs, RFCs, readmes, PR descriptions: Diátaxis + Google style + Global English. |
| [`/pstack-devin:control-ui`](./skills/control-ui/SKILL.md) | you want a local browser/CDP harness to drive and inspect a web or Electron UI. |
| [`/pstack-devin:control-cli`](./skills/control-cli/SKILL.md) | you want a tmux/PTY harness to drive and profile an interactive CLI or TUI. |

</details>

<details>
<summary>all twenty-four principles</summary>

`poteto-mode` indexes these inline and reads the full rule when one applies. Invoke one directly only to check it in isolation.

| principle | rule |
|---|---|
| [`attack-the-premise`](./skills/principle-attack-the-premise/SKILL.md) | two fixes sharing a premise failed the same gate: test the premise directly. |
| [`boundary-discipline`](./skills/principle-boundary-discipline/SKILL.md) | concentrate guards at system boundaries; keep interiors clean. |
| [`build-the-lever`](./skills/principle-build-the-lever/SKILL.md) | build the tool that does or proves the work, then pull it. |
| [`encode-lessons-in-structure`](./skills/principle-encode-lessons-in-structure/SKILL.md) | a correction made twice becomes a lint, type, or test. |
| [`exhaust-the-design-space`](./skills/principle-exhaust-the-design-space/SKILL.md) | no precedent: build competing prototypes, compare, pick. |
| [`experience-first`](./skills/principle-experience-first/SKILL.md) | user delight over implementation convenience. |
| [`explain-the-number`](./skills/principle-explain-the-number/SKILL.md) | never report or act on a number you can't explain. |
| [`fix-root-causes`](./skills/principle-fix-root-causes/SKILL.md) | trace each symptom to the first place the system went wrong. |
| [`foundational-thinking`](./skills/principle-foundational-thinking/SKILL.md) | settle core types and shared state before writing logic. |
| [`guard-the-context-window`](./skills/principle-guard-the-context-window/SKILL.md) | route bulk to subagents; keep the window for judgment. |
| [`laziness-protocol`](./skills/principle-laziness-protocol/SKILL.md) | bias toward deletion and the smallest working surface. |
| [`make-operations-idempotent`](./skills/principle-make-operations-idempotent/SKILL.md) | converge to the same end state however often a step runs. |
| [`migrate-callers-then-delete-legacy-apis`](./skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md) | migrate callers and delete the old API in the same wave. |
| [`minimize-reader-load`](./skills/principle-minimize-reader-load/SKILL.md) | count layers and hidden state between question and answer. |
| [`model-the-domain`](./skills/principle-model-the-domain/SKILL.md) | name the states and transitions before branching on them. |
| [`never-block-on-the-human`](./skills/principle-never-block-on-the-human/SKILL.md) | reversible work doesn't wait for permission. |
| [`outcome-oriented-execution`](./skills/principle-outcome-oriented-execution/SKILL.md) | converge on the target architecture at phase boundaries. |
| [`prove-it-works`](./skills/principle-prove-it-works/SKILL.md) | verify against the real artifact before declaring done. |
| [`redesign-from-first-principles`](./skills/principle-redesign-from-first-principles/SKILL.md) | new requirement: re-derive the design, don't bolt on. |
| [`separate-before-serializing-shared-state`](./skills/principle-separate-before-serializing-shared-state/SKILL.md) | eliminate shared state first; serialize structurally second. |
| [`sequence-verifiable-units`](./skills/principle-sequence-verifiable-units/SKILL.md) | break work into small units, each provable on its own. |
| [`subtract-before-you-add`](./skills/principle-subtract-before-you-add/SKILL.md) | remove dead code and stubs before adding anything. |
| [`test-behavior-not-implementation`](./skills/principle-test-behavior-not-implementation/SKILL.md) | assert what users observe, so the test fails only when behavior breaks. |
| [`type-system-discipline`](./skills/principle-type-system-discipline/SKILL.md) | make illegal states unrepresentable. |

</details>

For organization-wide install, install the repo URL under your org's plugin settings. Avoid also installing an uploaded copy — two installs register duplicate `pstack` skills, and uploads diverge from this repo's versioning.

## How it maps to Cursor

The adapter preserves pstack's content verbatim and rewrites only the harness surface. `docs/devin-mapping.tsv` has the full Cursor→Devin behavior mapping; the short version:

- `Task`/`subagent_type`/`environment: "cloud"` → `devin_session_create` child sessions (own VM, own git auth) — `readonly` and per-role model choices become advisory.
- `AskQuestion` → `message_user` user_question cards.
- Every delegate kickoff starts by reading `skills/poteto-mode/worker.md` (located with `find` on the child's VM).
- Model slugs (Opus 5.5 / Fable 5.2 / Gemini 4 Neon) → `devin_mode` (`normal` default, `fast` for mechanical and verification, `ultra` for the hardest work).
- Missing spawn capacity (quota, mode-lock) → the adapter prescribes serial fallback in-session.
- PR/review → `git_create_pr` / `fetch_pr_template` / Devin Review.

## Tracking upstream

`skills/` currently mirrors [backnotprop/pstack](https://github.com/backnotprop/pstack) at v0.15.44, which itself tracks [`cursor/plugins/pstack`](https://github.com/cursor/plugins/tree/main/pstack). To refresh:

```bash
./scripts/sync-upstream.sh            # from backnotprop/pstack main
./scripts/sync-upstream.sh --cursor   # straight from cursor/plugins (skips the mirror's own edits)
```

Review the diff, bump `version` in `.devin-plugin/plugin.json`, commit, and re-install the plugin (or re-upload it) to pick up changes.

This runs on its own: every Monday `.github/workflows/upstream-check.yml` opens an `upstream-sync` issue when upstream has a newer version, and a Devin Automation turns that issue into a sync PR. [docs/SYNCING.md](docs/SYNCING.md) has the steps.

## License

MIT — inherited from upstream ([Lauren Tan](LICENSE)). `skills/` is verbatim upstream content plus the `cursor-team-kit` ports noted above; adapter edits are in `skills/pstack/SKILL.md`.

---

<details>
<summary>日本語</summary>

[poteto-mode](https://github.com/backnotprop/pstack)（pstack）を Devin Cloud で動かすための単一 plugin。Devin は active な skill が1つだけなので、`poteto-mode` が内部で `how`/`architect` 等を invoke する設計がそのままでは噛み合わない。本 repo は全 leaf skill を `skills/` に同梱し、`@skills:pstack` 1本が内部参照で読む形に統合したアダプター。各 leaf skill は `/pstack-devin:<name>` として個別に invoke も可能（公式 port と同じ UX）。

インストール: Devin の Settings → Plugins からこの repo の URL を install → 任意のセッションで `@skills:pstack <タスク>`。leaf skill は `/pstack-devin:<name>`（例: `/pstack-devin:how`、`/pstack-devin:interrogate`）でも直接起動できる。全 skill/原理の一覧表は英語版 Usage 節参照。`/pstack-devin:poteto-mode` ではなく `/pstack-devin:pstack`（adapter）を使うこと——生 leaf は Devin の子セッション委譲を知らない。

</details>
