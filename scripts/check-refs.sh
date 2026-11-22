#!/usr/bin/env bash
# Verify that every path the adapter layer names still exists and that the
# version lives in one shape across plugin.json, README and CHANGELOG.
# Automates docs/SYNCING.md steps 5-6; run by .github/workflows/lint.yml.
# Every error names the fix.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
source scripts/adapter-skills.sh

fail=0
err() { echo "check-refs: ERROR: $*" >&2; fail=1; }

# Adapter-owned files that may name repo paths. CHANGELOG is historical and
# allowed to mention moved paths.
adapter_files() {
  find skills/pstack skills/deslop skills/control-cli skills/control-ui \
    scripts docs -type f ! -name check-refs.sh 2>/dev/null
  echo README.md
}

# --- Playbooks and agents the adapter SKILL.md names must exist -------------

missing="$(grep -oE 'playbooks/[a-z0-9-]+\.md' skills/pstack/SKILL.md | sort -u \
  | while read -r f; do
      [ -f "skills/poteto-mode/$f" ] || echo "$f"
    done)"
for f in $missing; do
  err "skills/pstack/SKILL.md references $f but skills/poteto-mode/$f is missing — add the playbook to skills/poteto-mode/playbooks/ or update the reference (docs/SYNCING.md step 5)"
done

missing="$(grep -oE '`agents/[a-z0-9-]+\.md`' skills/pstack/SKILL.md | tr -d '`' | sort -u \
  | while read -r f; do
      [ -f "skills/pstack/$f" ] || echo "$f"
    done)"
for f in $missing; do
  err "skills/pstack/SKILL.md references $f but skills/pstack/$f is missing — add the agent brief or update the reference"
done

[ -f skills/poteto-mode/worker.md ] || \
  err "skills/poteto-mode/worker.md is missing — the adapter's subagent kickoff line depends on it; restore it or update skills/pstack/SKILL.md"

# --- Adapter-owned skill dirs must exist ------------------------------------

for d in "${ADAPTER_SKILLS[@]}"; do
  [ -d "skills/$d" ] || \
    err "scripts/adapter-skills.sh lists '$d' but skills/$d/ does not exist — remove it from ADAPTER_SKILLS or restore the dir"
done

# --- Concrete skills/<dir>/ paths named in adapter files must exist ---------

missing="$(adapter_files | xargs grep -ohE 'skills/[a-z0-9-]+/' 2>/dev/null | sort -u \
  | while read -r d; do
      [ -d "$d" ] || echo "$d"
    done)"
for d in $missing; do
  err "an adapter file references $d but it does not exist — fix the reference or restore the dir (see 'adapter_files' in scripts/check-refs.sh for the scanned set)"
done

# --- The lib/ -> skills/ move must not regress ------------------------------

stale="$(adapter_files | xargs grep -lE '\blib/' 2>/dev/null || true)"
for f in $stale; do
  err "$f still mentions lib/ — the skill tree moved to skills/ in 0.15.44-devin.2; update the path (cf. ef02367)"
done

# --- One version, three places ----------------------------------------------

ver="$(jq -r .version .devin-plugin/plugin.json)"
if ! [[ "$ver" =~ ^[0-9]+\.[0-9]+\.[0-9]+-devin\.[0-9]+$ ]]; then
  err ".devin-plugin/plugin.json version '$ver' is not '<upstream semver>-devin.<N>' — fix the version (docs/SYNCING.md step 6)"
else
  upstream_ver="${ver%%-devin.*}"
  grep -q "v$upstream_ver" README.md || \
    err "README.md does not mention mirrored upstream v$upstream_ver — update the mirror line (docs/SYNCING.md step 6)"
  grep -q "^## $ver" CHANGELOG.md || \
    err "CHANGELOG.md has no '## $ver' entry — add one (docs/SYNCING.md step 6)"
fi

# --- Shell syntax ------------------------------------------------------------

for s in scripts/*.sh; do
  bash -n "$s" || err "$s fails bash -n"
done

if [ "$fail" -ne 0 ]; then
  echo "check-refs: FAILED" >&2
  exit 1
fi
echo "check-refs: all references resolve; versions agree."
