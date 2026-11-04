#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="\${GITHUB_WORKSPACE:?GITHUB_WORKSPACE is missing}"
SERVER_DIR="\${SERVER_DIR:?SERVER_DIR is missing}"
WORLD_NAME="\${WORLD_NAME:-survival}"
WORLD_SEED="\${WORLD_SEED:?WORLD_SEED is missing}"
WORLD_ID="\${WORLD_ID:?WORLD_ID is missing}"
WORLD_BRANCH="\${WORLD_BRANCH:?WORLD_BRANCH is missing}"
JOB_STARTED_EPOCH="\${JOB_STARTED_EPOCH:-$(date +%s)}"
HORIZON_BIN="\${HORIZON_BIN:-$(command -v horizon-server)}"
export HORIZON_BIN SERVER_DIR WORLD_NAME WORLD_SEED WORLD_ID WORLD_BRANCH

mkdir -p "$SERVER_DIR" "$SERVER_DIR/logs"
server_started=0
frpc_pid=""
telegram_pid=""
cleanup_started=0
cleanup_failed=0

notify() {
  python3 "$ROOT/scripts/notify.py" "$1" || true
}

horizon() {
  "$HORIZON_BIN" --dir "$SERVER_DIR" "$@"
}

cleanup() {
  local original_status=$?
  if [[ "$cleanup_started" == "1" ]]; then exit "$original_status"; fi
  cleanup_started=1
  trap - EXIT INT TERM
  set +e

  if [[ "$server_started" == "1" ]]; then
    echo "Starting graceful Horizon shutdown..."
    horizon cmd say "Server saving and stopping now. Your world progress is being checkpointed." \
      >> "$SERVER_DIR/logs/session.log" 2>&1
    horizon stop >> "$SERVER_DIR/logs/session.log" 2>&1
    phase="$(horizon status --json 2>/dev/null | jq -r '.phase // empty' 2>/dev/null)"
    if [[ "$phase" == "stopped" ]]; then
      echo "Horizon confirms stopped; creating final clean-shutdown snapshot."
      if python3 "$ROOT/scripts/world-data.py" final-snapshot; then
        notify "Horizon MC: final snapshot committed and verified. Server session ended cleanly."
      else
        echo "Final snapshot failed; previous remote snapshot remains the recovery point."
        notify "Horizon MC: WARNING - server stopped, but final snapshot failed. Restore will use the last verified checkpoint."
        cleanup_failed=1
      fi
    else
      echo "Horizon did not confirm a stopped phase. Refusing to mark this snapshot clean."
      notify "Horizon MC: WARNING - shutdown could not be confirmed. The latest hourly checkpoint remains the recovery point."
      cleanup_failed=1
    fi
  fi

  if [[ -n "$frpc_pid" ]]; then kill "$frpc_pid" 2>/dev/null; wait "$frpc_pid" 2>/dev/null; fi
  if [[ -n "$telegram_pid" ]]; then kill "$telegram_pid" 2>/dev/null; wait "$telegram_pid" 2>/dev/null; fi
  python3 "$ROOT/scripts/world-data.py" cleanup >/dev/null 2>&1

  if [[ "$original_status" -eq 0 && "$cleanup_failed" -ne 0 ]]; then original_status=1; fi
  exit "$original_status"
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

if [[ ! -f "$SERVER_DIR/server.toml" ]]; then
  echo "Initializing a new Horizon world with seed $WORLD_SEED."
  horizon init \
    --eula \
    --world "$WORLD_NAME" \
    --seed "$WORLD_SEED" \
    --port 25565 \
    --whitelist \
    --player "$OPERATOR_USERNAME" \
    --op "$OPERATOR_USERNAME" \
    --yes
fi

python3 "$ROOT/scripts/world-data.py" init
python3 "$ROOT/scripts/world-data.py" restore

# The backend listens only on loopback. The public Java route is FRP -> loopback.
horizon config set server.bind=127.0.0.1

echo "Starting Horizon..."
if horizon start; then
  server_started=1
else
  phase="$(horizon status --json 2>/dev/null | jq -r '.phase // empty' 2>/dev/null)"
  if [[ -n "$phase" && "$phase" != "stopped" ]]; then server_started=1; fi
  exit 1
fi

phase="$(horizon status --json | jq -r '.phase // empty')"
[[ "$phase" == "running" ]] || { echo "Horizon did not report phase=running (phase=$phase)."; exit 1; }

python3 "$ROOT/scripts/configure-frp.py"
"$FRP_DIR/frpc" -c "$FRP_DIR/frpc.toml" > "$FRP_DIR/frpc.log" 2>&1 &
frpc_pid=$!
sleep 5
kill -0 "$frpc_pid" || { cat "$FRP_DIR/frpc.log" || true; echo "FRP client exited during startup."; exit 1; }

if [[ -n "\${TELEGRAM_BOT_TOKEN:-}" && -n "\${TELEGRAM_ALLOWED_USER_IDS:-}" ]]; then
  python3 "$ROOT/scripts/telegram-bot.py" >> "$SERVER_DIR/logs/telegram-bot.log" 2>&1 &
  telegram_pid=$!
else
  echo "Telegram control disabled: configure token and numeric TELEGRAM_ALLOWED_USER_IDS."
fi

notify "Horizon MC is online. Java endpoint uses your FRP host on port 25565. Seed: $WORLD_SEED. Warnings at 5h00 and 5h15; graceful shutdown starts at 5h25."

job_start="$JOB_STARTED_EPOCH"
next_backup=$(( $(date +%s) + 3600 ))
first_warning_sent=0
second_warning_sent=0

while true; do
  now="$(date +%s)"
  elapsed=$(( now - job_start ))

  if [[ "$elapsed" -ge 300 && "$first_warning_sent" -eq 0 ]]; then
    horizon cmd say "Scheduled maintenance in 25 minutes. Please finish activities and return to a safe location." || true
    notify "Horizon MC: maintenance begins in 25 minutes (5h00 job elapsed)."
    first_warning_sent=1
  fi

  if [[ "$elapsed" -ge 315 && "$second_warning_sent" -eq 0 ]]; then
    horizon cmd say "Scheduled maintenance in 10 minutes. The server will save and stop at 5h25." || true
    notify "Horizon MC: 10-minute warning. Graceful shutdown starts at 5h25."
    second_warning_sent=1
  fi

  if [[ -f "$SERVER_DIR/.manual-stop" ]]; then
    echo "Manual Telegram stop requested."
    break
  fi

  if [[ "$elapsed" -ge 325 ]]; then
    echo "The 5h25 session limit has been reached; starting graceful shutdown."
    break
  fi

  phase="$(horizon status --json | jq -r '.phase // empty')"
  if [[ "$phase" != "running" ]]; then
    notify "Horizon MC: server left running phase unexpectedly (phase=$phase). Initiating recovery shutdown."
    echo "Unexpected Horizon phase: $phase"
    exit 1
  fi

  if ! kill -0 "$frpc_pid" 2>/dev/null; then
    notify "Horizon MC: FRP client exited. Shutting down safely; inspect FRP logs."
    cat "$FRP_DIR/frpc.log" || true
    exit 1
  fi

  if [[ "$now" -ge "$next_backup" ]]; then
    echo "Creating hourly checkpoint..."
    bash "$ROOT/scripts/checkpoint.sh"
    next_backup=$(( now + 3600 ))
  fi

  sleep 20
done

echo "Session time limit or manual stop reached. EXIT handler will save and shut down."
exit 0
