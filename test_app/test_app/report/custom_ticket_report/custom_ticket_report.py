# Copyright (c) 2026, soware and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns(filters)  # ⭐ Pass filters to get_columns
    data = get_grouped_data(filters)
    return columns, data

def get_columns(filters):
    columns = []
    
    # ⭐ Conditionally add "Assigned To" column only when grouping
    if filters.get("group_by_assignee"):
        columns.append({
            "label": "Assigned To", 
            "fieldname": "assigned_to", 
            "fieldtype": "Data", 
            "width": 200,
        })
    
    # Add remaining columns
    columns.extend([
        {"label": "Ticket ID", "fieldname": "name", "fieldtype": "Link", "options": "HD Ticket", "width": 120},
        {"label": "Created Date", "fieldname": "creation", "fieldtype": "Datetime", "width": 170},
        {"label": "Subject", "fieldname": "subject", "fieldtype": "Data", "width": 200},
        {"label": "Customer", "fieldname": "custom_customer_name", "fieldtype": "Link", "options": "HD Customer", "width": 150},
        {"label": "Phone Number", "fieldname": "custom_phone_number", "fieldtype": "Data", "width": 150},
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
    
    # Existing filter conditions (unchanged)
    if filters.get("from_date"):
        conditions += f" AND DATE(t.creation) >= {frappe.db.escape(filters.get('from_date'))}"
    if filters.get("to_date"):
        conditions += f" AND DATE(t.creation) <= {frappe.db.escape(filters.get('to_date'))}"
    if filters.get("status"):
        conditions += f" AND t.status = {frappe.db.escape(filters.get('status'))}"
    if filters.get("priority"):
        conditions += f" AND t.priority = {frappe.db.escape(filters.get('priority'))}"
    if filters.get("custom_customer_name"):
        conditions += f" AND t.custom_customer_name = {frappe.db.escape(filters.get('custom_customer_name'))}"
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

    # Main tickets query (consistent across both modes)
    tickets = frappe.db.sql(f"""
        SELECT
            t.name, t.creation, t.subject, t.custom_customer_name,
            t.custom_phone_number, t.agent_group, t.status, t.priority,
            t.custom_time_worked,
            (
                SELECT u.full_name FROM `tabToDo` a JOIN `tabUser` u ON u.name = a.allocated_to
                WHERE a.reference_type = 'HD Ticket' AND a.reference_name = t.name
                ORDER BY a.creation DESC LIMIT 1
            ) AS assignee_name,
            COALESCE(GROUP_CONCAT(DISTINCT c.content SEPARATOR ' || '), '') AS latest_comment
        FROM `tabHD Ticket` t
        LEFT JOIN `tabHD Ticket Comment` c ON c.reference_ticket = t.name
        WHERE {conditions}
        GROUP BY t.name
        ORDER BY assignee_name, t.creation DESC
    """, as_dict=True)

    # Check if Group By Assignee is enabled
    group_by_assignee = filters.get("group_by_assignee")
    
    if group_by_assignee:
        # GROUPED MODE: Headers + tickets per assignee
        grouped = {}
        for ticket in tickets:
            assignee = ticket.assignee_name or "Unassigned"
            if assignee not in grouped:
                grouped[assignee] = []
            grouped[assignee].append(ticket)

        final_data = []
        sl_no = 1
        
        for assignee, assignee_tickets in grouped.items():
            # Header row
            final_data.append({
                "assigned_to": assignee,      # Matches column order
                "name": "",
                "creation": "",
                "subject": "",
                "custom_customer_name": "",
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
            
            # Detail rows
            for ticket in assignee_tickets:
                ticket_copy = ticket.copy()
                ticket_copy["sl_no"] = sl_no
                ticket_copy["is_header"] = False
                final_data.append(ticket_copy)
                sl_no += 1
                
        return final_data
    else:
        # FLAT MODE: Old format - simple list with sl_no
        final_data = []
        sl_no = 1
        for ticket in tickets:
            ticket_copy = ticket.copy()
            ticket_copy["sl_no"] = sl_no
            final_data.append(ticket_copy)
            sl_no += 1
        return final_data