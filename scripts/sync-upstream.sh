#!/usr/bin/env bash
# Sync lib/ (and the bundled poteto-mode extras) from upstream pstack.
#   ./scripts/sync-upstream.sh            # backnotprop/pstack main (the mirror)
#   ./scripts/sync-upstream.sh --cursor   # cursor/plugins pstack (skips mirror edits)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${1:-}"

if [[ "$SRC" == "--cursor" ]]; then
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  git clone --depth 1 --filter=blob:none --sparse https://github.com/cursor/plugins.git "$TMP/cursor-plugins"
  git -C "$TMP/cursor-plugins" sparse-checkout set pstack
  UPSTREAM_SKILLS="$TMP/cursor-plugins/pstack/skills"
else
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  git clone --depth 1 https://github.com/backnotprop/pstack.git "$TMP/pstack"
  UPSTREAM_SKILLS="$TMP/pstack/skills"
fi

# Every leaf skill -> lib/<name>/ (verbatim, tree structure kept so references/ resolve)
rsync -a --delete --exclude .git "$UPSTREAM_SKILLS/" "$REPO_ROOT/lib/"

# poteto-mode's own extras -> skills/pstack/{playbooks,references,scripts}
for dir in playbooks references scripts; do
  if [[ -d "$UPSTREAM_SKILLS/poteto-mode/$dir" ]]; then
    rsync -a --delete "$UPSTREAM_SKILLS/poteto-mode/$dir/" "$REPO_ROOT/skills/pstack/$dir/"
  fi
done

# repo-root agents/ -> skills/pstack/agents/ (the subagent briefs the adapter maps onto devin_session_create)
UPSTREAM_AGENTS="${UPSTREAM_SKILLS%/skills}/agents"
if [[ -d "$UPSTREAM_AGENTS" ]]; then
  rsync -a --delete "$UPSTREAM_AGENTS/" "$REPO_ROOT/skills/pstack/agents/"
fi

echo "Synced from ${SRC:-backnotprop/pstack}. Review the diff, bump .devin-plugin/plugin.json version, commit, and re-install."
git -C "$REPO_ROOT" status --short | head -30
