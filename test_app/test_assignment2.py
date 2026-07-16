import frappe

def execute():
    task = frappe.get_doc("Payment Collection Task", "PCT-00010")
    print(f"Assigning tasks to {task.assigned_to}")
    
    other_tasks = frappe.get_all(
        "Payment Collection Task",
        filters={
            "customer": task.customer,
            "status": ["in", ["Open", "In Progress"]],
            "name": ["!=", task.name]
        },
        fields=["name"]
    )
    
    for ot in other_tasks:
        frappe.db.set_value("Payment Collection Task", ot.name, "assigned_to", task.assigned_to)
        print(f"Assigned {ot.name} to {task.assigned_to}")
        
    frappe.db.commit()
