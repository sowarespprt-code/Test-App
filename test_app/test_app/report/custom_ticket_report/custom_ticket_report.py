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
        {"label": "Ticket ID", "fieldname": "name", "fieldtype": "Link", "options": "HD Ticket", "width": 120},
        {"label": "Created Date", "fieldname": "creation", "fieldtype": "Datetime", "width": 170},
        {"label": "Subject", "fieldname": "subject", "fieldtype": "Data", "width": 200},
        {"label": "Customer", "fieldname": "custom_customer_name", "fieldtype": "Link", "options": "HD Customer", "width": 150},
        {"label": "Phone Number", "fieldname": "custom_phone_number", "fieldtype": "Data", "width": 150},
        {"label": "Team", "fieldname": "agent_group", "fieldtype": "Link", "options": "HD Team", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": "Priority", "fieldname": "priority", "fieldtype": "Data", "width": 120},
        {"label": "Assigned To", "fieldname": "assigned_to", "fieldtype": "Data", "width": 150},
        {"label": "Latest Comment", "fieldname": "latest_comment", "fieldtype": "Data", "width": 300},
        {"label": "Time Worked", "fieldname": "custom_time_worked", "fieldtype": "Data", "width": 120},

    ]


def get_data(filters):
    conditions = "1=1"

    # Filter by dates
    if filters.get("from_date"):
        conditions += f" AND DATE(t.creation) >= '{filters.get('from_date')}'"
    if filters.get("to_date"):
        conditions += f" AND DATE(t.creation) <= '{filters.get('to_date')}'"


    # Optional filters
    if filters.get("status"):
        conditions += f" AND t.status = '{filters.get('status')}'"
    if filters.get("priority"):
        conditions += f" AND t.priority = '{filters.get('priority')}'"
    if filters.get("custom_customer_name"):
        conditions += f" AND t.custom_customer_name = '{filters.get('custom_customer_name')}'"
    if filters.get("assigned_to"):
        conditions += f"""
            AND (
                SELECT a.allocated_to
                FROM `tabToDo` a
                WHERE a.reference_type = 'HD Ticket'
                AND a.reference_name = t.name
                ORDER BY a.creation DESC
                LIMIT 1
            ) = {frappe.db.escape(filters.get("assigned_to"))}
        """
    if filters.get("agent_group"):
        conditions += f" AND t.agent_group = {frappe.db.escape(filters.get('agent_group'))}"


    return frappe.db.sql(f"""
        SELECT
            t.name,
            t.creation,
            t.subject,
            t.custom_customer_name,
            t.custom_phone_number,
            t.agent_group,
            t.status,
            t.priority,
            -- ✅ FIXED: Get LATEST assignee by MAX creation time
            (SELECT u.full_name 
            FROM `tabToDo` a 
            JOIN `tabUser` u ON u.name = a.allocated_to
            WHERE a.reference_type = 'HD Ticket' 
            AND a.reference_name = t.name
            ORDER BY a.creation DESC 
            LIMIT 1) AS assigned_to,
            t.custom_time_worked,
            COALESCE(GROUP_CONCAT(DISTINCT c.content SEPARATOR ' || '), '') AS latest_comment
        FROM `tabHD Ticket` t
        LEFT JOIN `tabHD Ticket Comment` c
            ON c.reference_ticket = t.name
        WHERE {conditions}
        GROUP BY t.name
        ORDER BY t.creation DESC
    """, as_dict=True)






