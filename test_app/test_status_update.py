import frappe
from test_app.api import log_management_call

def execute():
    # Find an open task
    task = frappe.get_all("Payment Collection Task", filters={"status": "Open"}, limit=1)
    if not task:
        print("No open tasks found.")
        return
    
    task_id = task[0].name
    print(f"Testing on task: {task_id}")
    
    # Log a call
    log_management_call(
        task_id=task_id,
        discussion_summary="Test Summary",
        customer_response="Test Response"
    )
    
    # Check status
    doc = frappe.get_doc("Payment Collection Task", task_id)
    print(f"Status after log: {doc.status}")
