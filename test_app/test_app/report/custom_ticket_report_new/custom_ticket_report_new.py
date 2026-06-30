# Copyright (c) 2026, soware and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    filters = filters or {}
    columns = get_columns(filters)
    data = get_grouped_data(filters)
    return columns, data


def get_columns(filters):
    columns = []

    if filters.get("group_by_assignee"):
        columns.append({
            "label": "Assigned To",
            "fieldname": "assigned_to",
            "fieldtype": "Data",
            "width": 200,
        })

    columns.extend([
        {"label": "Ticket ID", "fieldname": "name", "fieldtype": "Link", "options": "HD Ticket", "width": 120},
        {"label": "Created Date", "fieldname": "creation", "fieldtype": "Datetime", "width": 170},
        {"label": "Customer", "fieldname": "customer_display_name", "fieldtype": "Data", "width": 180},
        {"label": "Contact Person", "fieldname": "custom_contactperson", "fieldtype": "Data", "width": 180},
        {"label": "Phone Number", "fieldname": "custom_phone_number", "fieldtype": "Data", "width": 150},
        {"label": "Subject", "fieldname": "subject", "fieldtype": "Data", "width": 200},
        {"label": "Team", "fieldname": "agent_group", "fieldtype": "Link", "options": "HD Team", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": "Priority", "fieldname": "priority", "fieldtype": "Data", "width": 120},
        {"label": "Assignee", "fieldname": "assignee_name", "fieldtype": "Data", "width": 150},
        {"label": "Latest Comment", "fieldname": "latest_comment", "fieldtype": "Data", "width": 300},
        {"label": "Time Worked", "fieldname": "custom_time_worked", "fieldtype": "Data", "width": 120},
    ])

    return columns


def get_grouped_data(filters):
    conditions = "1=1"

    if filters.get("from_date"):
        conditions += f" AND DATE(t.creation) >= {frappe.db.escape(filters.get('from_date'))}"

    if filters.get("to_date"):
        conditions += f" AND DATE(t.creation) <= {frappe.db.escape(filters.get('to_date'))}"

    if filters.get("status"):
        conditions += f" AND t.status = {frappe.db.escape(filters.get('status'))}"

    if filters.get("priority"):
        conditions += f" AND t.priority = {frappe.db.escape(filters.get('priority'))}"

    if filters.get("custom_customer_name"):
        conditions += f""" AND (
            t.customer = {frappe.db.escape(filters.get('custom_customer_name'))}
            OR t.custom_customer_name = {frappe.db.escape(filters.get('custom_customer_name'))}
        )"""

    if filters.get("assigned_to"):
        conditions += f"""
            AND (
                SELECT a.allocated_to
                FROM `tabToDo` a
                WHERE a.reference_type = 'HD Ticket' AND a.reference_name = t.name
                ORDER BY a.creation DESC LIMIT 1
            ) = {frappe.db.escape(filters.get("assigned_to"))}
        """

    if filters.get("agent_group"):
        conditions += f" AND t.agent_group = {frappe.db.escape(filters.get('agent_group'))}"

    tickets = frappe.db.sql(f"""
        SELECT
            t.name,
            t.creation,
            COALESCE(hc.customer_name, t.custom_customer_name, t.customer) AS customer_display_name,
            t.custom_contactperson,
            t.custom_phone_number,
            t.subject,
            t.agent_group,
            t.status,
            t.priority,
            t.custom_time_worked,
            (
                SELECT u.full_name
                FROM `tabToDo` a
                JOIN `tabUser` u ON u.name = a.allocated_to
                WHERE a.reference_type = 'HD Ticket' AND a.reference_name = t.name
                ORDER BY a.creation DESC LIMIT 1
            ) AS assignee_name,
            COALESCE(GROUP_CONCAT(DISTINCT c.content SEPARATOR ' || '), '') AS latest_comment
        FROM `tabHD Ticket` t
        LEFT JOIN `tabHD Customer` hc ON hc.name = t.customer
        LEFT JOIN `tabHD Ticket Comment` c ON c.reference_ticket = t.name
        WHERE {conditions}
        GROUP BY t.name
        ORDER BY assignee_name, t.creation DESC
    """, as_dict=True)

    if filters.get("group_by_assignee"):
        grouped = {}
        for ticket in tickets:
            assignee = ticket.get("assignee_name") or "Unassigned"
            grouped.setdefault(assignee, []).append(ticket)

        final_data = []
        sl_no = 1

        for assignee, assignee_tickets in grouped.items():
            final_data.append({
                "assigned_to": assignee,
                "name": "",
                "creation": "",
                "subject": "",
                "customer_display_name": "",
                "custom_contactperson" : "",
                "custom_phone_number": "",
                "agent_group": "",
                "status": "",
                "priority": "",
                "assignee_name": assignee,
                "latest_comment": "",
                "custom_time_worked": "",
                "sl_no": "",
                "is_header": True,
                "ticket_count": len(assignee_tickets)
            })

            for ticket in assignee_tickets:
                row = ticket.copy()
                row["sl_no"] = sl_no
                row["is_header"] = False
                final_data.append(row)
                sl_no += 1

        return final_data

    final_data = []
    sl_no = 1
    for ticket in tickets:
        row = ticket.copy()
        row["sl_no"] = sl_no
        final_data.append(row)
        sl_no += 1

    return final_data