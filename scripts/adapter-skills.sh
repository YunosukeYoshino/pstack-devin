# shellcheck shell=bash
# skills/ subdirectories that are NOT mirrored from upstream pstack:
# pstack is the Devin adapter; deslop, control-cli and control-ui are
# cursor-team-kit ports (via pstack-ports/devin-pstack, synced by hand).
# sync-upstream.sh keeps them; check-upstream.sh excludes them from the
# upstream inventory; check-refs.sh verifies they exist. One list, one
# place — scripts must source this file, never restate the names.
ADAPTER_SKILLS=(pstack deslop control-cli control-ui)
