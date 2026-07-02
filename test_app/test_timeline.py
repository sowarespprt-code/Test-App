import frappe
def test():
    for dt in ["Payment Collection Task", "Call Management Task"]:
        doc = frappe.get_doc("DocType", dt)
        print(f"{dt}: track_changes={doc.track_changes}, track_views={doc.track_views}")
        doc.track_changes = 1
        doc.track_views = 1
        doc.save()
    frappe.db.commit()
    print("Enabled track_changes and track_views")
