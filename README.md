# pstack-devin

[poteto-mode](https://github.com/backnotprop/pstack) (pstack) as a single Devin Cloud plugin — the full skill library bundled for Devin's one-active-skill model.

## Why this exists

Devin keeps exactly **one skill active** at a time: invoking another skill replaces the active one ([Devin docs](https://docs.devin.ai/product-guides/skills)). pstack's design is the opposite — `poteto-mode` routes internally to `how`, `architect`, `swarm`, `tdd`, `interrogate`, and ~40 sibling skills, expecting each to become active on demand.

`pstack-devin` resolves that mismatch with a structural adapter:

- **`skills/pstack/SKILL.md`** — the one skill Devin activates (`@skills:pstack`). It contains poteto-mode's philosophy verbatim (non-negotiables, principles, autonomy, writing rules, playbook index) plus a Devin adapter-rules section that replaces skill-invocation with file reads, and Devin-native mappings for subagents, questions, and review.
- **`lib/`** — the complete pstack skill library (all 46 leaf skills, verbatim from upstream). When the adapter routes to "the `how` skill", the session reads `lib/how/SKILL.md` as a file instead of invoking a skill — so routing never disturbs the active skill.
- **`skills/pstack/{playbooks,references,scripts,agents}`** — poteto-mode's 23 playbooks and supporting files, verbatim.

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

For organization-wide install, install the repo URL under your org's plugin settings. Avoid also installing an uploaded copy — two installs register duplicate `pstack` skills, and uploads diverge from this repo's versioning.

## How it maps to Cursor

The adapter preserves pstack's content verbatim and rewrites only the harness surface. `docs/devin-mapping.tsv` has the full 22-row Cursor→Devin behavior mapping; the short version:

- `Task`/`subagent_type`/`environment: "cloud"` → `devin_session_create` child sessions (own VM, own git auth) — `readonly` and per-role model choices become advisory.
- `AskQuestion` → `message_user` user_question cards.
- Missing spawn capacity (quota, mode-lock) → the adapter prescribes serial fallback in-session.
- PR/review → `git_create_pr` / `fetch_pr_template` / Devin Review.

## Tracking upstream

`lib/` currently mirrors [backnotprop/pstack](https://github.com/backnotprop/pstack) at v0.15.2, which itself tracks [`cursor/plugins/pstack`](https://github.com/cursor/plugins/tree/main/pstack). To refresh:

```bash
./scripts/sync-upstream.sh            # from backnotprop/pstack main
./scripts/sync-upstream.sh --cursor   # straight from cursor/plugins (skips the mirror's own edits)
```

Review the diff, bump `version` in `.devin-plugin/plugin.json`, commit, and re-install the plugin (or re-upload it) to pick up changes.

## License

MIT — inherited from upstream ([Lauren Tan](LICENSE)). `lib/` is verbatim upstream content; adapter edits are in `skills/pstack/SKILL.md`.

---

<details>
<summary>日本語</summary>

[poteto-mode](https://github.com/backnotprop/pstack)（pstack）を Devin Cloud で動かすための単一 plugin。Devin は active な skill が1つだけなので、`poteto-mode` が内部で `how`/`architect` 等を invoke する設計がそのままでは噛み合わない。本 repo は全 leaf skill を `lib/` に同梱し、`@skills:pstack` 1本が内部参照で読む形に統合したアダプター。

インストール: Devin の Settings → Plugins からこの repo の URL を install → 任意のセッションで `@skills:pstack <タスク>`。詳細は上記英語版どおり。

</details>
