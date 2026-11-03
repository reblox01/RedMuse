#!/bin/sh
# RedMuse update check. Prints one line per tracked source:
#   name | local | latest | status
# Statuses: up-to-date, update-available, unreachable, manual, skipped.
# This script never rewrites skill content and never pushes. It only
# reports. A fast-forward pull of RedMuse itself is a separate step
# the orchestrator takes after seeing update-available.
# Usage: ./tools/check_updates.sh [repo-dir]

ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"

# RedMuse itself: local HEAD vs origin/main HEAD. A fetch is
# read-only for the working tree; it only refreshes remote refs so
# behind, ahead, and diverged can be told apart.
if git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1; then
  LOCAL=$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo unknown)
  FETCH_OK=0
  if git -C "$ROOT" fetch -q origin 2>/dev/null; then
    FETCH_OK=1
    REMOTE=$(git -C "$ROOT" rev-parse origin/main 2>/dev/null || echo unknown)
  else
    REMOTE=$(git ls-remote https://github.com/reblox01/RedMuse.git HEAD 2>/dev/null | awk '{print $1}')
  fi
  if [ -z "$REMOTE" ] || [ "$REMOTE" = unknown ]; then
    echo "redmuse | $LOCAL | unknown | unreachable"
  elif [ "$LOCAL" = "$REMOTE" ]; then
    echo "redmuse | $LOCAL | $REMOTE | up-to-date"
  elif [ "$FETCH_OK" = 1 ] && git -C "$ROOT" merge-base --is-ancestor "$LOCAL" "$REMOTE" 2>/dev/null; then
    echo "redmuse | $LOCAL | $REMOTE | update-available"
  elif [ "$FETCH_OK" = 1 ] && git -C "$ROOT" merge-base --is-ancestor "$REMOTE" "$LOCAL" 2>/dev/null; then
    echo "redmuse | $LOCAL | $REMOTE | ahead (unpushed commits, pull is a no-op)"
  elif [ "$FETCH_OK" = 1 ]; then
    echo "redmuse | $LOCAL | $REMOTE | diverged (stop, do not force)"
  else
    echo "redmuse | $LOCAL | $REMOTE | unknown-relation (fetch failed, pull manually)"
  fi
else
  echo "redmuse | unknown | unknown | skipped (not a git checkout)"
fi

# Strix methodology reference: upstream HEAD only, never vendored.
STRIX=$(git ls-remote https://github.com/usestrix/strix.git HEAD 2>/dev/null | awk '{print $1}')
if [ -z "$STRIX" ]; then
  echo "strix | reference-only | unknown | unreachable"
else
  echo "strix | reference-only | $STRIX | manual-review-if-changed"
fi

# Securly reference: upstream HEAD only, never vendored.
SECURY=$(git ls-remote https://github.com/BghitCode/Securly.git HEAD 2>/dev/null | awk '{print $1}')
if [ -z "$SECURY" ]; then
  echo "securly | reference-only | unknown | unreachable"
else
  echo "securly | reference-only | $SECURY | manual-review-if-changed"
fi

# Cloudflare: no version endpoint, no bundled skill. Always manual.
echo "cloudflare | original-checklist | none | manual"
