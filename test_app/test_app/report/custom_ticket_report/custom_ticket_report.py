import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)

    # Add SL NO column sequence
    for idx, row in enumerate(data, start=1):
        row["sl_no"] = idx

    return columns, data


def get_columns():
    return [
        {"label": "SL No", "fieldname": "sl_no", "fieldtype": "Int", "width": 80},
        {"label": "Ticket ID", "fieldname": "name", "fieldtype": "Link", "options": "HD Ticket", "width": 120},
        {"label": "Created Date", "fieldname": "creation", "fieldtype": "Datetime", "width": 170},
        {"label": "Subject", "fieldname": "subject", "fieldtype": "Data", "width": 200},
        {"label": "Customer", "fieldname": "custom_customer_name", "fieldtype": "Link", "options": "HD Customer", "width": 150},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": "Priority", "fieldname": "priority", "fieldtype": "Data", "width": 120},
        {"label": "Owner", "fieldname": "owner", "fieldtype": "Data", "width": 120},
    ]


def get_data(filters):
    conditions = "1=1"

    # Filter by dates
    if filters.get("from_date"):
        conditions += f" AND DATE(creation) >= '{filters.get('from_date')}'"
    if filters.get("to_date"):
        conditions += f" AND DATE(creation) <= '{filters.get('to_date')}'"

    # Optional filters
    if filters.get("status"):
        conditions += f" AND status = '{filters.get('status')}'"
    if filters.get("priority"):
        conditions += f" AND priority = '{filters.get('priority')}'"
    if filters.get("custom_customer_name"):
        conditions += f" AND custom_customer_name = '{filters.get('custom_customer_name')}'"

    return frappe.db.sql(f"""
        SELECT
            name, creation, subject, custom_customer_name,
            status, priority, owner
        FROM `tabHD Ticket`
        WHERE {conditions}
        ORDER BY creation DESC
    """, as_dict=True)
