#!/bin/bash
set -e

BENCH="/home/soware/frappe-bench"
APP_DIR="$BENCH/apps/helpdesk"
OVERRIDES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Resetting Helpdesk to clean state ==="
cd "$APP_DIR"
git checkout .

echo "=== Copying all custom files ==="
cp -rv "$OVERRIDES_DIR/src/"* "$APP_DIR/desk/src/"

echo "=== Installing dependencies ==="
yarn add leaflet -W

echo "=== Building frontend ==="
cd "$APP_DIR/desk"
yarn install
NODE_OPTIONS="--max-old-space-size=4096" yarn build

echo "=== DONE! Live site updated successfully ==="
