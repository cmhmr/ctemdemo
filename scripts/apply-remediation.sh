#!/usr/bin/env bash
# Apply a CTEM remediation patch (training demo helper).
#
# Usage:
#   scripts/apply-remediation.sh --list
#   scripts/apply-remediation.sh CTEM-SAST-01            # apply one scenario
#   scripts/apply-remediation.sh --check CTEM-SAST-01    # dry run
#   scripts/apply-remediation.sh --all                   # apply every patch
#
# Patches live in remediation/patches/ and touch only the files of their own
# scenario (code + its regression test), so they can be applied independently
# and in any order. Commit each one separately to tell the remediation story.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PATCH_DIR="$ROOT/remediation/patches"
cd "$ROOT"

usage() { sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

apply_patch() {
  local file="$1"; shift
  local args=("$@")
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    # Patches use paths relative to this project root; when the project lives
    # in a subdirectory of a larger repository, prefix them accordingly.
    local prefix
    prefix="$(git rev-parse --show-prefix)"
    if [[ -n "$prefix" ]]; then args+=("--directory=${prefix%/}"); fi
    git apply "${args[@]}" "$file"
  else
    if [[ " ${args[*]-} " == *" --check "* ]]; then
      patch -p1 --dry-run < "$file"
    else
      patch -p1 < "$file"
    fi
  fi
}

check=()
case "${1:-}" in
  ""|-h|--help) usage 0 ;;
  --list) ls -1 "$PATCH_DIR" | sed 's/\.patch$//'; exit 0 ;;
  --check) check=(--check); shift; [[ $# -ge 1 ]] || usage 1 ;;
esac

if [[ "$1" == "--all" ]]; then
  patches=("$PATCH_DIR"/*.patch)
else
  shopt -s nullglob
  patches=("$PATCH_DIR/$1"*.patch)
  [[ ${#patches[@]} -eq 1 ]] || { echo "Expected exactly one patch matching '$1' (found ${#patches[@]}). Use --list." >&2; exit 1; }
fi

for p in "${patches[@]}"; do
  apply_patch "$p" "${check[@]}"
  echo "${check:+[check] }applied: $(basename "$p")"
done
