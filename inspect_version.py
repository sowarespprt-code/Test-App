import frappe
import json

def execute():
    versions = frappe.get_all("Version", filters={"ref_doctype": "Payment Collection Task"}, fields=["name", "data"])
    for v in versions:
        data = json.loads(v.data)
        if "added" in data:
            print("ADDED format:", data["added"])
            break
