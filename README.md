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

インストール: Devin の Settings → Plugins からこの repo の URL を install → 任意のセッションで `@skills:pstack <タスク>`。詳細は上記英語版どおり。

</details>
