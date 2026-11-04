#!/usr/bin/env bash
set -Eeuo pipefail

: "${SERVER_DIR:?SERVER_DIR is missing}"
: "${WORLD_NAME:=survival}"
: "${WORLD_SEED:?WORLD_SEED is missing}"
HORIZON_BIN="${HORIZON_BIN:-$(command -v horizon-server)}"

args=(
  --dir "$SERVER_DIR"
  init
  --eula
  --world "$WORLD_NAME"
  --seed "$WORLD_SEED"
  --port 25565
  --whitelist
  --yes
)

if [[ -n "${OPERATOR_USERNAME:-}" ]]; then
  args+=(--player "$OPERATOR_USERNAME" --op "$OPERATOR_USERNAME")
else
  echo "No operator username supplied; initializing with an empty whitelist and no operators."
fi

exec "$HORIZON_BIN" "${args[@]}"
