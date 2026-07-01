import frappe

def force_export():
    doc = frappe.get_doc("DocType", "Call Management Log")
    doc.custom = 0
    doc.module = "Test App"
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    print("Forced export of Call Management Log")
