import frappe
def execute():
    for dt in ["Payment Collection Task", "Call Management Log"]:
        doc = frappe.get_doc("DocType", dt)
        if not doc.track_changes or not doc.track_views:
            doc.track_changes = 1
            doc.track_views = 1
            doc.save()
            print(f"Enabled tracking for {dt}")
    frappe.db.commit()
    print("Done")
