import frappe

def execute():
    task = frappe.get_doc("Payment Collection Task", "PCT-00010")
    print("Task customer:", task.customer)

    other_tasks = frappe.get_all(
        "Payment Collection Task",
        filters={
            "customer": task.customer,
            "status": ["in", ["Open", "In Progress"]],
            "name": ["!=", task.name]
        },
        fields=["name", "assigned_to"]
    )
    print("Other tasks:", other_tasks)
