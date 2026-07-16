import frappe

def execute():
    meta = frappe.get_meta("Call Management Task")
    for f in meta.fields:
        print(f.fieldname)
