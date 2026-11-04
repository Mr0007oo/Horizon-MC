#!/usr/bin/env bash
set -Eeuo pipefail

: "${SERVER_DIR:?SERVER_DIR is missing}"
mkdir -p "$SERVER_DIR"
exec 9>"$SERVER_DIR/.checkpoint.lock"
if ! flock -n 9; then
  echo "A checkpoint is already in progress; this request was not completed." >&2
  exit 75
fi

if ! python3 "$GITHUB_WORKSPACE/scripts/world-data.py" snapshot; then
  python3 "$GITHUB_WORKSPACE/scripts/notify.py" \
    "Horizon MC: checkpoint FAILED. The previous verified remote snapshot was preserved; no continuation will be attempted." || true
  exit 1
fi

python3 "$GITHUB_WORKSPACE/scripts/notify.py" "Horizon MC: hourly world checkpoint committed and verified." || true
