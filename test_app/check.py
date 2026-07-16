import frappe
def execute():
    meta = frappe.get_meta("Payment Collection Call History")
    for f in meta.fields:
        print(f.fieldname)
