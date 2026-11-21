#!/usr/bin/env bash
# Sync skills/<leaf>/ from upstream pstack (poteto-mode's own extras included).
# Managed-outside-upstream skill dirs are kept: pstack/ (the adapter) and
# deslop/ control-cli/ control-ui/ (ported from cursor-team-kit via
# pstack-ports/devin-pstack — sync those by hand from that repo).
#   ./scripts/sync-upstream.sh            # backnotprop/pstack main (the mirror)
#   ./scripts/sync-upstream.sh --cursor   # cursor/plugins pstack (skips mirror edits)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MODE="${1:-}"

case "$MODE" in
  ""|--cursor) ;;
  *) echo "usage: $0 [--cursor]" >&2; exit 2 ;;
esac

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if [[ "$MODE" == "--cursor" ]]; then
  git clone --depth 1 --filter=blob:none --sparse https://github.com/cursor/plugins.git "$TMP/cursor-plugins"
  git -C "$TMP/cursor-plugins" sparse-checkout set pstack
  UPSTREAM_SKILLS="$TMP/cursor-plugins/pstack/skills"
else
  git clone --depth 1 https://github.com/backnotprop/pstack.git "$TMP/pstack"
  UPSTREAM_SKILLS="$TMP/pstack/skills"
fi

# Every leaf skill -> skills/<name>/ (verbatim, tree structure kept so
# references/ resolve; each leaf is also directly invocable as /<plugin>:<name>).
# Exclude dirs that don't come from upstream pstack.
rsync -a --delete --exclude .git \
  --exclude 'pstack/' --exclude 'deslop/' --exclude 'control-cli/' --exclude 'control-ui/' \
  "$UPSTREAM_SKILLS/" "$REPO_ROOT/skills/"

# repo-root agents/ -> skills/pstack/agents/ (the subagent briefs the adapter maps onto devin_session_create)
UPSTREAM_AGENTS="${UPSTREAM_SKILLS%/skills}/agents"
if [[ -d "$UPSTREAM_AGENTS" ]]; then
  rsync -a --delete "$UPSTREAM_AGENTS/" "$REPO_ROOT/skills/pstack/agents/"
fi

echo "Synced from ${MODE:-backnotprop/pstack}. Review the diff, bump .devin-plugin/plugin.json version, commit, and re-install."
git -C "$REPO_ROOT" status --short | head -30
