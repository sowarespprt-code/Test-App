import frappe

def patch():
    doc = frappe.get_doc("DocType", "Payment Collection Task")
    for field in doc.fields:
        if field.fieldname == "assigned_to":
            field.reqd = 0
            print("Changed assigned_to reqd to 0 for Payment Collection Task")
    doc.save()
    frappe.db.commit()

patch()
