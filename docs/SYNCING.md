# Syncing from upstream

`skills/` mirrors [backnotprop/pstack](https://github.com/backnotprop/pstack). Every Monday `.github/workflows/upstream-check.yml` runs `scripts/check-upstream.sh`. When upstream's `plugin.json` version is newer than ours, it opens an issue labeled `upstream-sync`. A Devin Automation picks that label up and follows the steps below. A human can follow the same steps.

## Steps

1. Branch from `main`: `devin/<unix-ts>-sync-upstream-<version>`.
2. Run `./scripts/sync-upstream.sh`. It copies upstream verbatim into `skills/` (excluding `skills/pstack` and the `deslop`/`control-cli`/`control-ui` ports) and repo-root `agents/` into `skills/pstack/agents`. Never hand-edit upstream-synced paths.
3. Re-apply poteto-mode changes to the adapter. `skills/pstack/SKILL.md` is upstream's `poteto-mode/SKILL.md` plus Devin edits.
   - Read `git diff main -- skills/poteto-mode/SKILL.md`.
   - Carry every upstream change into the matching section of `skills/pstack/SKILL.md` (Non-negotiables, Principles, Autonomy, Subagents, Writing the reply, Comments, Playbooks). Keep upstream's wording.
   - Keep the Devin edits: the frontmatter, **Devin adapter rules**, **Harness**, the model mapping, and `$PSTACK_SKILLS` / `$PSTACK_DIR` paths.
4. Cover new Cursor-only constructs. Search the new upstream text for harness terms:

   ```bash
   git diff main -- skills | grep -nE '^\+.*(\.cursor/|agent-transcripts|cursor-team-kit|create-skill|AskQuestion|subagent_type|\bTask\b|/loop|model[- ]name)'
   ```

   For each term the **Harness** section or the adapter rules do not already map, add a mapping there and a row in `docs/devin-mapping.tsv`. Do not edit upstream-synced files under `skills/`.
5. Check that every path the adapter names still exists:

   ```bash
   ./scripts/check-refs.sh
   ```

   It covers the playbook list, agent briefs, adapter-owned dirs, `skills/` paths, stale references to the pre-`skills` layout, and version drift between `plugin.json`, `README.md` and `CHANGELOG.md`. CI runs it on every PR. Add new playbooks to the **Playbooks** list. Remove deleted ones.
6. Set `version` in `.devin-plugin/plugin.json` to `<upstream>-devin.1`, update the mirrored version in `README.md`, and add a `CHANGELOG.md` entry: upstream version, new or removed skills, adapter changes. `check-refs.sh` fails if the three disagree.
7. Open a PR whose body says `Closes #<issue>`. Run Devin Review and resolve every thread. Do not merge: the owner merges.
8. Comment the PR link on the issue.
