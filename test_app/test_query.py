import frappe
import json

def execute():
    customer = "TEST_1"
    
    tasks = frappe.get_all("Payment Collection Task", filters={"customer": customer}, fields=["name"])
    task_names = [t.name for t in tasks]
    
    if not task_names:
        print("No tasks")
        return
        
    calls = frappe.get_all("Payment Collection Call Log", filters={"parent": ["in", task_names]}, fields=["*", "parent"])
    print("Calls length:", len(calls))
    if calls:
        print("Sample call:", calls[0])
