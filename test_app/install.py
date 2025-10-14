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
        "NewCustomerDialog.vue": "desk/src/components/desk/global/NewCustomerDialog.vue",
        "CustomerDialog.vue": "desk/src/pages/desk/customer/CustomerDialog.vue",
        "TicketNew.vue":"desk/src/pages/ticket/TicketNew.vue"
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