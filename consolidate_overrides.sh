#!/bin/bash
set -e

# ============================================================
# CONSOLIDATION SCRIPT
# Copies all real working Vue/TS files from overrides/ into 
# frontend_overrides/src/ with correct helpdesk folder paths.
# Python files are NOT touched — they stay in overrides/ for backend.
# ============================================================

BENCH="/home/user/test-bench"
OVERRIDES="$BENCH/apps/test_app/test_app/overrides"
DEST="$BENCH/apps/test_app/test_app/frontend_overrides/src"

echo "Creating folder structure..."
mkdir -p $DEST/components/desk/global
mkdir -p $DEST/components/layouts
mkdir -p $DEST/components/ticket-agent
mkdir -p $DEST/components/ticket
mkdir -p $DEST/pages/ticket
mkdir -p $DEST/pages/desk/customer
mkdir -p $DEST/router

echo ""
echo "Copying files with correct target paths..."

# --- COMPONENTS (go into desk/src/components/) ---
cp -v "$OVERRIDES/ListRows.vue"            "$DEST/components/ListRows.vue"
cp -v "$OVERRIDES/ListViewBuilder.vue"     "$DEST/components/ListViewBuilder.vue"

# NewCustomerDialog goes into components/desk/global/
cp -v "$OVERRIDES/NewCustomerDialog.vue"   "$DEST/components/desk/global/NewCustomerDialog.vue"

# layoutSettings goes into components/layouts/
cp -v "$OVERRIDES/layoutSettings.ts"       "$DEST/components/layouts/layoutSettings.ts"

# ticket-agent components
cp -v "$OVERRIDES/TicketActivityPanel.vue"  "$DEST/components/ticket-agent/TicketActivityPanel.vue"
cp -v "$OVERRIDES/TicketDetailsTab.vue"     "$DEST/components/ticket-agent/TicketDetailsTab.vue"

# ticket components
cp -v "$OVERRIDES/ActivityHeader.vue"       "$DEST/components/ticket/ActivityHeader.vue"
cp -v "$OVERRIDES/TicketAgentActivities.vue" "$DEST/components/ticket/TicketAgentActivities.vue"
cp -v "$OVERRIDES/TicketAgentFields.vue"    "$DEST/components/ticket/TicketAgentFields.vue"

# --- PAGES (go into desk/src/pages/) ---
cp -v "$OVERRIDES/Tickets.vue"              "$DEST/pages/ticket/Tickets.vue"
cp -v "$OVERRIDES/TicketAgent.vue"          "$DEST/pages/ticket/TicketAgent.vue"
cp -v "$OVERRIDES/TicketNew.vue"            "$DEST/pages/ticket/TicketNew.vue"
cp -v "$OVERRIDES/MobileTicketAgent.vue"    "$DEST/pages/ticket/MobileTicketAgent.vue"
cp -v "$OVERRIDES/CustomerDialog.vue"       "$DEST/pages/desk/customer/CustomerDialog.vue"
cp -v "$OVERRIDES/Customers.vue"            "$DEST/pages/desk/customer/Customers.vue"

# Custom NEW pages (already in helpdesk/desk/src/pages via test_app)
# These are already handled by the pages/ folder in frontend_overrides

# --- ROUTER ---
cp -v "$OVERRIDES/index.ts"                 "$DEST/router/index.ts"

echo ""
echo "✅ All Vue/TS files consolidated into frontend_overrides/src/"
echo ""
echo "Python files (.py) remain in overrides/ for the Frappe backend."
echo ""
echo "Now updating patch_helpdesk_ui.sh..."

# Rewrite patch_helpdesk_ui.sh to be 100% safe (no patch command)
cat > "$BENCH/apps/test_app/test_app/frontend_overrides/patch_helpdesk_ui.sh" << 'SCRIPT'
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
SCRIPT

chmod +x "$BENCH/apps/test_app/test_app/frontend_overrides/patch_helpdesk_ui.sh"

echo "✅ patch_helpdesk_ui.sh updated — no more patch command!"
echo ""
echo "Next steps:"
echo "  cd /home/user/test-bench/apps/test_app"
echo "  git add ."
echo '  git commit -m "Consolidate all Vue overrides into frontend_overrides/src"'
echo "  git push origin newbranch"
