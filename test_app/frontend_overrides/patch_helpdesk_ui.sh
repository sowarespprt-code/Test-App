#!/bin/bash
set -e

# Auto-detect bench root from script location (works on any machine)
# Script is at: <BENCH>/apps/test_app/test_app/frontend_overrides/patch_helpdesk_ui.sh
# So going 4 levels up gives us the bench root.
OVERRIDES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCH="$(cd "$OVERRIDES_DIR/../../../.." && pwd)"
APP_DIR="$BENCH/apps/helpdesk"

echo "=== Detected bench: $BENCH ==="
echo "=== Helpdesk path: $APP_DIR ==="
echo "=== Overrides path: $OVERRIDES_DIR ==="

# Verify helpdesk app exists
if [ ! -d "$APP_DIR" ]; then
  echo "ERROR: Helpdesk app not found at $APP_DIR"
  exit 1
fi

echo ""
echo "=== Resetting Helpdesk to clean state ==="
cd "$APP_DIR"
git checkout .

echo ""
echo "=== Copying all custom files ==="
cp -rv "$OVERRIDES_DIR/src/"* "$APP_DIR/desk/src/"

echo ""
echo "=== Installing dependencies ==="
yarn add leaflet -W

echo ""
echo "=== Building frontend ==="
cd "$APP_DIR/desk"
yarn install
NODE_OPTIONS="--max-old-space-size=4096" yarn build

echo ""
echo "=== DONE! Site updated successfully ==="
