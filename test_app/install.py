#!/usr/bin/env python3
import os
import shutil

def install_overrides():
    """Copy override files to Helpdesk"""
    
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    overrides_dir = os.path.join(script_dir, "overrides")
    
    # Navigate to bench directory
    bench_dir = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
    helpdesk_dir = os.path.join(bench_dir, "apps", "helpdesk")
    
    print(f"Script directory: {script_dir}")
    print(f"Overrides directory: {overrides_dir}")
    print(f"Bench directory: {bench_dir}")
    print(f"Helpdesk directory: {helpdesk_dir}")
    
    if not os.path.exists(overrides_dir):
        print(f"❌ Overrides directory not found: {overrides_dir}")
        return False
        
    if not os.path.exists(helpdesk_dir):
        print(f"❌ Helpdesk app not found: {helpdesk_dir}")
        return False
    
    # File mappings
    files = {
        "layoutSettings.ts": "desk/src/components/layouts/layoutSettings.ts",
        "ProductList.vue": "desk/src/pages/ProductList.vue",
        "ProductDetail.vue": "desk/src/pages/ProductDetail.vue",
        "CustomerAlertList.vue" : "desk/src/pages/CustomerAlertList.vue",
        "CustomerAlertDetail.vue" : "desk/src/pages/CustomerAlertDetail.vue",
        "NewCustomerDialog.vue": "desk/src/components/desk/global/NewCustomerDialog.vue",
        "CustomerDialog.vue": "desk/src/pages/desk/customer/CustomerDialog.vue",
        "TicketNew.vue":"desk/src/pages/ticket/TicketNew.vue",
        "license.py":"helpdesk/api/license.py",
        # "TicketAgentFields.vue":"desk/src/components/ticket/TicketAgentFields.vue",
        # "TicketAgent.vue":"desk/src/pages/ticket/TicketAgent.vue",
        "TicketDetailsTab.vue":"desk/src/components/ticket-agent/TicketDetailsTab.vue",
        "TicketHeader.vue" : "desk/src/components/ticket-agent/TicketHeader.vue",
        "LicenseDetailsPopup.vue":"desk/src/components/LicenseDetailsPopup.vue",
        "CustomerSearchPopup.vue":"desk/src/components/CustomerSearchPopup.vue",
        "CustomerRemarksPopup.vue" : "desk/src/components/CustomerRemarksPopup.vue",
        "ListRows.vue" : "desk/src/components/ListRows.vue",
        "ListViewBuilder.vue" : "desk/src/components/ListViewBuilder.vue",
        "Tickets.vue" : "desk/src/pages/ticket/Tickets.vue",
        
        # "api.py":"helpdesk/helpdesk/doctype/hd_ticket/api.py",
        # "TicketCustomerSidebar.vue":"desk/src/components/ticket/TicketCustomerSidebar.vue",
        "hd_customer.py":"helpdesk/helpdesk/doctype/hd_customer/hd_customer.py",
        "hd_ticket.py":"helpdesk/helpdesk/doctype/hd_ticket/hd_ticket.py",
        "customer_api.py":"helpdesk/api/customer_api.py",
        "index.ts": "desk/src/router/index.ts",
        "doc.py" : "helpdesk/api/doc.py",
        "App.vue" : "desk/src/App.vue"
    }
    
    success = True
    for source_file, dest_path in files.items():
        source = os.path.join(overrides_dir, source_file)
        destination = os.path.join(helpdesk_dir, dest_path)
        
        if not os.path.exists(source):
            print(f"⚠️  Source not found: {source}")
            continue
            
        # Backup original
        if os.path.exists(destination):
            backup = destination + ".original"
            if not os.path.exists(backup):
                shutil.copy2(destination, backup)
                print(f"💾 Backed up: {dest_path}")
        
        # Copy file
        try:
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.copy2(source, destination)
            print(f"✅ Copied: {dest_path}")
        except Exception as e:
            print(f"❌ Failed to copy {source_file}: {e}")
            success = False
    
    if success:
        print("\n✅ All files copied successfully!")
        print("\n🔧 Next steps:")
        print("   cd apps/helpdesk/desk")
        print("   yarn build")
        print("   cd ~/test-bench")
        print("   bench restart")
        return True
    else:
        print("\n❌ Some files failed to copy")
        return False

if __name__ == "__main__":
    install_overrides()