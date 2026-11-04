#!/usr/bin/env bash
set -Eeuo pipefail

: "${GH_TOKEN:?GitHub token missing}"
: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is missing}"
: "${HORIZON_RESOURCES_RELEASE_TAG:=resources-26.3}"
: "${HORIZON_RESOURCES_ASSET:=horizon-resources-26.3.tar.gz}"
: "${HORIZON_DATA_DIR:?HORIZON_DATA_DIR is missing}"

api="https://api.github.com/repos/${GITHUB_REPOSITORY}/releases/tags/${HORIZON_RESOURCES_RELEASE_TAG}"
headers=(-H "Authorization: Bearer ${GH_TOKEN}" -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28")
release="$(curl -fsSL "${headers[@]}" "$api")"

asset_id="$(jq -r --arg name "$HORIZON_RESOURCES_ASSET" '.assets[] | select(.name == $name) | .id' <<<"$release" | head -n1)"
checksum_name="${HORIZON_RESOURCES_ASSET}.sha256"
checksum_id="$(jq -r --arg name "$checksum_name" '.assets[] | select(.name == $name) | .id' <<<"$release" | head -n1)"

[[ "$asset_id" =~ ^[0-9]+$ ]] || {
  echo "::error::Private release $HORIZON_RESOURCES_RELEASE_TAG has no $HORIZON_RESOURCES_ASSET asset."
  exit 1
}
[[ "$checksum_id" =~ ^[0-9]+$ ]] || {
  echo "::error::Private release must also contain $checksum_name."
  exit 1
}

mkdir -p "$RUNNER_TEMP/horizon-resources"
asset_url="https://api.github.com/repos/${GITHUB_REPOSITORY}/releases/assets/${asset_id}"
checksum_url="https://api.github.com/repos/${GITHUB_REPOSITORY}/releases/assets/${checksum_id}"

curl -fsSL -L "${headers[@]}" -H "Accept: application/octet-stream" "$asset_url" \
  -o "$RUNNER_TEMP/horizon-resources/$HORIZON_RESOURCES_ASSET"
curl -fsSL -L "${headers[@]}" -H "Accept: application/octet-stream" "$checksum_url" \
  -o "$RUNNER_TEMP/horizon-resources/$checksum_name"

cd "$RUNNER_TEMP/horizon-resources"
sha256sum --check "$checksum_name"
python3 "$GITHUB_WORKSPACE/scripts/prepare-resources.py" \
  "$HORIZON_RESOURCES_ASSET" \
  "$HORIZON_DATA_DIR/game-files/horizon-client"

rm -f "$HORIZON_RESOURCES_ASSET" "$checksum_name"
