#!/bin/bash
APP_DIR="/home/user/test-bench/apps/helpdesk"
OVERRIDES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Copying custom Vue components to Helpdesk..."
cp -R $OVERRIDES_DIR/src/* $APP_DIR/desk/src/

echo "Applying UI patches to Helpdesk router and layouts..."
cd $APP_DIR
# We use --forward so it doesn't fail if already applied
patch -p1 --forward < $OVERRIDES_DIR/helpdesk_ui.patch || true

echo "Installing missing dependencies..."
yarn add leaflet -W

echo "Rebuilding Helpdesk frontend..."
cd $APP_DIR/desk
yarn install
NODE_OPTIONS="--max-old-space-size=4096" yarn build

echo "Helpdesk UI patched successfully!"
