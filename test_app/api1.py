import frappe

@frappe.whitelist()
def get_ticket_button_visibility(ticket_name):
    try:
        ticket = frappe.get_doc("HD Ticket", ticket_name)
        current_user = frappe.session.user
        
        # ✅ RULE 1: Closed → NO BUTTON
        if ticket.status == "Closed":
            return {
                "show_button": 0,
                "button_text": "",
                "is_close": 0
            }
        
        # ✅ RULE 2: Not Assigned / Other → ALWAYS Start Ticket
        if ticket.status in ["Not Assigned", "Other"]:
            return {
                "show_button": 1,
                "button_text": "Start Ticket",
                "is_close": 0
            }
        
        # Latest ToDo (for In Progress/etc.)
        todos = frappe.get_all("ToDo", 
            filters={
                "reference_type": "HD Ticket", 
                "reference_name": ticket_name,
                "status": "Open" 
            },
            fields=["allocated_to"],
            order_by="creation desc",
            limit=1
        )
        
        assignee_email = todos[0].allocated_to if todos else None
        
        # ✅ RULE 3: No assignee → Start Ticket
        if not assignee_email:
            return {
                "show_button": 1,
                "button_text": "Start Ticket",
                "is_close": 0
            }
        
        # Check admin/assignee
        user_roles = frappe.get_roles(current_user)
        is_admin = "Administrator" in user_roles
        
        if assignee_email == current_user or is_admin:
            return {
                "show_button": 1,
                "button_text": "Close Ticket",
                "is_close": 1
            }
        
        # Others see assigned message
        try:
            assignee_name = frappe.db.get_value("User", assignee_email, "full_name") or assignee_email
        except:
            assignee_name = assignee_email
        
        return {
            "show_button": 0,
            "button_text": f"Assigned to {assignee_name}",
            "is_close": 0
        }
        
    except Exception:
        # Fallback
        return {
            "show_button": 1,
            "button_text": "Start Ticket",
            "is_close": 0
        }

@frappe.whitelist()
def start_ticket(ticket_name):
    """Atomic ticket start - NO DUPLICATES even with concurrent clicks"""
    current_user = frappe.session.user
    
    # ✅ ATOMIC LOCK: Prevents concurrent access
    ticket = frappe.get_doc("HD Ticket", ticket_name, for_update=True)
    
    # ✅ CHECK ALL Open ToDos (not just current user)
    existing_todos = frappe.get_all("ToDo", 
        filters={
            "reference_type": "HD Ticket",
            "reference_name": ticket_name,
            "status": "Open"
        },
        fields=["allocated_to"],
        limit=1
    )
    
    if existing_todos:
        # ✅ ANY existing assignee blocks (even other users)
        assignee_email = existing_todos[0].allocated_to
        assignee_name = frappe.db.get_value("User", assignee_email, "full_name") or assignee_email
        return {
            "show_alert": 1,
            "message": f"You cannot start this ticket because {assignee_name} is assigned",
            "assignee": assignee_name
        }
    
    # ✅ SAFE: No existing ToDo → Create new one + update ticket
    todo = frappe.get_doc({
        "doctype": "ToDo",
        "reference_type": "HD Ticket",
        "reference_name": ticket_name,
        "allocated_to": current_user,
        "description": f"Started working on ticket {ticket_name}",
        "status": "Open"
    })
    todo.insert()
    
    ticket.status = "In Progress"  # Or "Progressing"
    ticket.custom_start_time = frappe.utils.now_datetime()
    ticket.save()
    
    frappe.db.commit()
    return {"message": "Ticket started successfully"}

@frappe.whitelist()
def get_ticket_assignment_alert(ticket_name):
    try:
        # Get LATEST active ToDo
        todos = frappe.get_all("ToDo", 
            filters={
                "reference_type": "HD Ticket",
                "reference_name": ticket_name,
                "status": "Open"  # Active only
            },
            fields=["allocated_to"],
            order_by="creation desc",  # Latest first
            limit=1
        )
        
        if not todos:
            return {"show_alert": 0, "message": "", "assignee": ""}
        
        assignee_email = todos[0].allocated_to
        assignee_name = frappe.db.get_value("User", assignee_email, "full_name") or assignee_email
        
        current_user = frappe.session.user
        user_roles = frappe.get_roles(current_user)
        is_admin = "Administrator" in user_roles
        
        # Show if NOT current user AND not admin
        if assignee_email != current_user and not is_admin:
            return {
                "show_alert": 1,
                "message": f"Ticket is assigned to {assignee_name}",
                "assignee": assignee_name
            }
        
        return {"show_alert": 0, "message": "", "assignee": ""}
    except Exception as e:
        frappe.log_error(f"Alert error {ticket_name}: {str(e)}")
        return {"show_alert": 0, "message": "", "assignee": ""}


