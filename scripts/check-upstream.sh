#!/usr/bin/env bash
# Open an `upstream-sync` issue when backnotprop/pstack ships a version newer than skills/.
# Run by .github/workflows/upstream-check.yml; needs GH_TOKEN with issues:write.
set -euo pipefail

UPSTREAM="${UPSTREAM:-backnotprop/pstack}"
LABEL="${LABEL:-upstream-sync}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

local_full="$(jq -r .version "$REPO_ROOT/.devin-plugin/plugin.json")"
local_ver="${local_full%%-devin.*}"
upstream_ver="$(gh api "repos/$UPSTREAM/contents/plugin.json" --jq .content | base64 -d | jq -r .version)"
upstream_sha="$(gh api "repos/$UPSTREAM/commits/main" --jq .sha)"

echo "local=$local_ver upstream=$upstream_ver"
if [[ "$local_ver" == "$upstream_ver" ]] || \
   [[ "$(printf '%s\n%s\n' "$local_ver" "$upstream_ver" | sort -V | tail -1)" == "$local_ver" ]]; then
  echo "Up to date."
  exit 0
fi

REPO="${GITHUB_REPOSITORY:-YunosukeYoshino/pstack-devin}"
open_issue="$(gh issue list -R "$REPO" --label "$LABEL" --state open --json number --jq '.[0].number // empty')"
if [[ -n "$open_issue" ]]; then
  # The title's trailing version records the latest version already notified.
  if gh issue view "$open_issue" -R "$REPO" --json title --jq .title | grep -qE " ${upstream_ver//./\\.}\$"; then
    echo "Issue #$open_issue already tracks $upstream_ver."
    exit 0
  fi
  comment="Upstream moved to **$upstream_ver** (\`${upstream_sha:0:7}\`). Sync to the latest upstream when working this issue."
  if [[ -n "${DRY_RUN:-}" ]]; then
    printf 'Would retitle #%s and comment:\n%s\n' "$open_issue" "$comment"
    exit 0
  fi
  gh issue edit "$open_issue" -R "$REPO" --title "Sync upstream pstack $local_ver → $upstream_ver"
  gh issue comment "$open_issue" -R "$REPO" --body "$comment"
  echo "Retitled and commented on #$open_issue."
  exit 0
fi

upstream_skills="$(gh api "repos/$UPSTREAM/contents/skills" --jq '.[] | select(.type=="dir") | .name' | sort)"
local_skills="$(find "$REPO_ROOT/lib" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort)"
added="$(comm -13 <(echo "$local_skills") <(echo "$upstream_skills") | sed 's/^/- `/; s/$/`/')"
removed="$(comm -23 <(echo "$local_skills") <(echo "$upstream_skills") | sed 's/^/- `/; s/$/`/')"

upstream_poteto_sha="$(gh api "repos/$UPSTREAM/contents/skills/poteto-mode/SKILL.md" --jq .sha)"
local_poteto_sha="$(git -C "$REPO_ROOT" hash-object skills/poteto-mode/SKILL.md)"
if [[ "$upstream_poteto_sha" == "$local_poteto_sha" ]]; then
  poteto="No. \`skills/pstack/SKILL.md\` only needs a check for new leaf references."
else
  poteto="**Yes.** Re-apply the upstream changes to \`skills/pstack/SKILL.md\`."
fi

[[ -n "${DRY_RUN:-}" ]] || gh label create "$LABEL" -R "$REPO" --color 1d76db --description "Upstream pstack has a newer version" 2>/dev/null || true

body="$(cat <<MD
Upstream [\`$UPSTREAM\`](https://github.com/$UPSTREAM) is at **$upstream_ver** (\`${upstream_sha:0:7}\`). \`lib/\` is at **$local_ver**.

Follow [docs/SYNCING.md](https://github.com/${GITHUB_REPOSITORY:-YunosukeYoshino/pstack-devin}/blob/main/docs/SYNCING.md).

**poteto-mode SKILL.md changed:** $poteto

**New skills**
${added:-none}

**Removed skills**
${removed:-none}

What changed: [SYNC-LOG.md](https://github.com/$UPSTREAM/blob/main/SYNC-LOG.md)
MD
)"

if [[ -n "${DRY_RUN:-}" ]]; then
  printf '%s\n\n%s\n' "Sync upstream pstack $local_ver → $upstream_ver" "$body"
  exit 0
fi

gh issue create -R "$REPO" --title "Sync upstream pstack $local_ver → $upstream_ver" --label "$LABEL" --body "$body"
