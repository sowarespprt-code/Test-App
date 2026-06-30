# import json
# import frappe
# from frappe.desk.form.assign_to import add as add_assignment 

# NOT_ASSIGNED_STATUS = "Not Assigned"
# IN_PROGRESS_STATUS = "In Progress"

# # def auto_assign_on_status_change(doc, method):
# #     """
# #     Handle status changes - but ONLY if NOT triggered by Start Ticket button
# #     ✅ Skip if flag `via_start_ticket_button` is set
# #     """
# #     if doc.is_new():
# #         return
    
# #     # ✅ CRITICAL: Skip if this change came from Start Ticket button
# #     if doc.flags.get("via_start_ticket_button"):
# #         print(f"⏭️ Skipping auto-assign logic (triggered by Start Ticket button)")
# #         return

# #     old = doc.get_doc_before_save()
# #     if not old:
# #         return

# #     # 🔴 FORCE CLEAR ASSIGNEES when status MANUALLY changed to Not Assigned
# #     if old.status != NOT_ASSIGNED_STATUS and doc.status == NOT_ASSIGNED_STATUS:
# #         print(f"🧹 Manual status change to Not Assigned → Force clearing assignments")
# #         _force_clear_all_assignments(doc)
# #         return

#     # # Status MANUALLY changed FROM Not Assigned to something else
#     # if old.status == NOT_ASSIGNED_STATUS and doc.status != NOT_ASSIGNED_STATUS:
#     #     if frappe.session.user == "Administrator":
#     #         return

#     #     existing_assignments = frappe.get_all(
#     #         "ToDo",
#     #         filters={
#     #             "reference_type": doc.doctype,
#     #             "reference_name": doc.name,
#     #             "status": ["!=", "Cancelled"],
#     #         },
#     #         limit=1,
#     #     )

#     #     if existing_assignments:
#     #         return

#     #     print(f"➕ Manual status change from Not Assigned → Auto-assigning to {frappe.session.user}")
#     #     add_assignment(
#     #         {
#     #             "doctype": doc.doctype,
#     #             "name": doc.name,
#     #             "assign_to": [frappe.session.user],
#     #             "description": f"Auto-assigned on status change to {doc.status}",
#     #         }
#     #     )


# def clear_ticket_todo_on_unassign(doc, method):
#     """
#     🔴 Force clear ALL assignments when manually removed from UI
#     ✅ Skip if triggered by Start Ticket button
#     """
#     # ✅ Skip if this is from Start Ticket button
#     if doc.flags.get("via_start_ticket_button"):
#         print(f"⏭️ Skipping unassign logic (triggered by Start Ticket button)")
#         return
    
#     # Only run when _assign field changes
#     if not doc.has_value_changed("_assign"):
#         return

#     # Get current assignment state
#     assign_raw = doc.get("_assign") or "[]"
#     try:
#         assigned_users = json.loads(assign_raw) if isinstance(assign_raw, str) else assign_raw
#         assigned_users = [u for u in assigned_users if u and u.strip()]
#     except Exception:
#         assigned_users = []

#     print(f"🔍 Manual Assignment Change Detected for {doc.name}")
#     print(f"   Current _assign: {assigned_users}")

#     # 🔴 IF NO ASSIGNEES → FORCE CLEAR EVERYTHING
#     if not assigned_users:
#         print(f"   ⚠️ NO ASSIGNEES → Forcing complete clear")
#         _force_clear_all_assignments(doc)
#     else:
#         # Clean up ToDos for users who were removed
#         _cleanup_removed_user_todos(doc, assigned_users)


# def _force_clear_all_assignments(doc):
#     """
#     🔴 NUCLEAR OPTION: Complete forceful clear
#     """
#     print(f"💥 FORCE CLEARING all assignments for {doc.name}")
    
#     # 1️⃣ Cancel ALL existing ToDo assignments
#     todos = frappe.get_all(
#         "ToDo",
#         filters={
#             "reference_type": doc.doctype,
#             "reference_name": doc.name,
#             "status": ["!=", "Cancelled"],
#         },
#         pluck="name",
#     )
    
#     print(f"   📋 Cancelling {len(todos)} ToDos")
#     for todo in todos:
#         frappe.db.set_value("ToDo", todo, "status", "Cancelled")
    
#     # 2️⃣ Clear assignment cache (_assign) - FORCE to None
#     doc._assign = None
#     frappe.db.set_value(doc.doctype, doc.name, "_assign", None)
#     print(f"   🧹 Cleared _assign field")
    
#     # 3️⃣ Ensure no reassignment happens in same save
#     frappe.db.commit()
#     print(f"   ✅ Committed changes")


# def _cleanup_removed_user_todos(doc, current_assigned_users):
#     """Clean up ToDos for users who are NO LONGER in the assignment list"""
#     todos = frappe.get_all(
#         "ToDo",
#         filters={
#             "reference_type": doc.doctype,
#             "reference_name": doc.name,
#             "status": ["!=", "Cancelled"],
#         },
#         fields=["name", "allocated_to"]
#     )
    
#     for todo in todos:
#         if todo.allocated_to not in current_assigned_users:
#             print(f"   ❌ Cancelling ToDo {todo.name} for removed user {todo.allocated_to}")
#             frappe.db.set_value("ToDo", todo.name, "status", "Cancelled")
    
#     if todos:
#         frappe.db.commit()


# def handle_start_ticket_assignment(doc, method):
#     if not doc.flags.get("via_start_ticket_button"):
#         return

#     if frappe.session.user == "Administrator":
#         return

#     print(f"🚀 Start Ticket button clicked for {doc.name} by {frappe.session.user}")

#     # 1. Cancel ALL existing ToDos
#     todos = frappe.get_all(
#         "ToDo",
#         filters={
#             "reference_type": "HD Ticket",
#             "reference_name": doc.name,
#             "status": ["!=", "Cancelled"],
#         },
#         pluck="name",
#     )
#     for todo_name in todos:
#         frappe.db.set_value("ToDo", todo_name, "status", "Cancelled")

#     # 2. Clear _assign
#     frappe.db.set_value("HD Ticket", doc.name, "_assign", "[]")
#     doc._assign = []

#     # 3. Create NEW ToDo for current user
#     todo = frappe.get_doc({
#         "doctype": "ToDo",
#         "reference_type": "HD Ticket",
#         "reference_name": doc.name,
#         "status": "Open",
#         "allocated_to": frappe.session.user,
#         "description": f"Started by {frappe.session.user}",
#         "priority": "Medium"
#     })
#     todo.insert(ignore_permissions=True)

#     # 4. Update _assign
#     frappe.db.set_value("HD Ticket", doc.name, "_assign", json.dumps([frappe.session.user]))
#     doc._assign = [frappe.session.user]

#     # 5. Ensure status flag
#     if doc.status != IN_PROGRESS_STATUS:
#         doc.status = IN_PROGRESS_STATUS

#     frappe.db.commit()



# def notify_ticket_status_change(doc, method):
#     """Notify frontend on status change"""
#     if doc.has_value_changed("status"):
#         frappe.publish_realtime("doc_update", {
#             "doctype": doc.doctype,
#             "doc": doc.name,
#             "status": doc.status
#         }, user=frappe.session.user)


# def prevent_frappe_auto_assignment(doc, method):
#     """Block Frappe's built-in assignment handlers"""
#     doc.flags.ignore_auto_assignment = True





import json
import frappe
from frappe.desk.form.assign_to import add as add_assignment 

NOT_ASSIGNED_STATUS = "Not Assigned"
IN_PROGRESS_STATUS = "In Progress"

def auto_assign_on_status_change(doc, method):
    """
    Handle status changes - but ONLY if NOT triggered by Start Ticket button
    ✅ Skip if flag `via_start_ticket_button` is set
    """
    if doc.is_new():
        return
    
    # ✅ CRITICAL: Skip if this change came from Start Ticket button
    if doc.flags.get("via_start_ticket_button"):
        print(f"⏭️ Skipping auto-assign logic (triggered by Start Ticket button)")
        return

    old = doc.get_doc_before_save()
    if not old:
        return

    # 🔴 FORCE CLEAR ASSIGNEES when status MANUALLY changed to Not Assigned
    if old.status != NOT_ASSIGNED_STATUS and doc.status == NOT_ASSIGNED_STATUS:
        print(f"🧹 Manual status change to Not Assigned → Force clearing assignments")
        _force_clear_all_assignments(doc)
        return

    # # Status MANUALLY changed FROM Not Assigned to something else
    # if old.status == NOT_ASSIGNED_STATUS and doc.status != NOT_ASSIGNED_STATUS:
    #     if frappe.session.user == "Administrator":
    #         return

    #     existing_assignments = frappe.get_all(
    #         "ToDo",
    #         filters={
    #             "reference_type": doc.doctype,
    #             "reference_name": doc.name,
    #             "status": ["!=", "Cancelled"],
    #         },
    #         limit=1,
    #     )

    #     if existing_assignments:
    #         return

    #     print(f"➕ Manual status change from Not Assigned → Auto-assigning to {frappe.session.user}")
    #     add_assignment(
    #         {
    #             "doctype": doc.doctype,
    #             "name": doc.name,
    #             "assign_to": [frappe.session.user],
    #             "description": f"Auto-assigned on status change to {doc.status}",
    #         }
    #     )


def clear_ticket_todo_on_unassign(doc, method):
    """
    🔴 Force clear ALL assignments when manually removed from UI
    ✅ Skip if triggered by Start Ticket button
    """
    # ✅ Skip if this is from Start Ticket button
    if doc.flags.get("via_start_ticket_button"):
        print(f"⏭️ Skipping unassign logic (triggered by Start Ticket button)")
        return
    
    # Only run when _assign field changes
    if not doc.has_value_changed("_assign"):
        return

    # Get current assignment state
    assign_raw = doc.get("_assign") or "[]"
    try:
        assigned_users = json.loads(assign_raw) if isinstance(assign_raw, str) else assign_raw
        assigned_users = [u for u in assigned_users if u and u.strip()]
    except Exception:
        assigned_users = []

    print(f"🔍 Manual Assignment Change Detected for {doc.name}")
    print(f"   Current _assign: {assigned_users}")

    # 🔴 IF NO ASSIGNEES → FORCE CLEAR EVERYTHING
    if not assigned_users:
        print(f"   ⚠️ NO ASSIGNEES → Forcing complete clear")
        _force_clear_all_assignments(doc)
    else:
        # Clean up ToDos for users who were removed
        _cleanup_removed_user_todos(doc, assigned_users)


def _force_clear_all_assignments(doc):
    """
    🔴 NUCLEAR OPTION: Complete forceful clear
    """
    print(f"💥 FORCE CLEARING all assignments for {doc.name}")
    
    # 1️⃣ Cancel ALL existing ToDo assignments
    todos = frappe.get_all(
        "ToDo",
        filters={
            "reference_type": doc.doctype,
            "reference_name": doc.name,
            "status": ["!=", "Cancelled"],
        },
        pluck="name",
    )
    
    print(f"   📋 Cancelling {len(todos)} ToDos")
    for todo in todos:
        frappe.db.set_value("ToDo", todo, "status", "Cancelled")
    
    # 2️⃣ Clear assignment cache (_assign) - FORCE to None
    doc._assign = None
    frappe.db.set_value(doc.doctype, doc.name, "_assign", None)
    print(f"   🧹 Cleared _assign field")
    
    # 3️⃣ Ensure no reassignment happens in same save
    frappe.db.commit()
    print(f"   ✅ Committed changes")


def _cleanup_removed_user_todos(doc, current_assigned_users):
    """Clean up ToDos for users who are NO LONGER in the assignment list"""
    todos = frappe.get_all(
        "ToDo",
        filters={
            "reference_type": doc.doctype,
            "reference_name": doc.name,
            "status": ["!=", "Cancelled"],
        },
        fields=["name", "allocated_to"]
    )
    
    for todo in todos:
        if todo.allocated_to not in current_assigned_users:
            print(f"   ❌ Cancelling ToDo {todo.name} for removed user {todo.allocated_to}")
            frappe.db.set_value("ToDo", todo.name, "status", "Cancelled")
    
    if todos:
        frappe.db.commit()


def handle_start_ticket_assignment(doc, method):
    if not doc.flags.get("via_start_ticket_button"):
        return

    if frappe.session.user == "Administrator":
        return

    print(f"🚀 Start Ticket button clicked for {doc.name} by {frappe.session.user}")

    # 1. Cancel ALL existing ToDos
    todos = frappe.get_all(
        "ToDo",
        filters={
            "reference_type": "HD Ticket",
            "reference_name": doc.name,
            "status": ["!=", "Cancelled"],
        },
        pluck="name",
    )
    for todo_name in todos:
        frappe.db.set_value("ToDo", todo_name, "status", "Cancelled")

    # 2. Clear _assign
    frappe.db.set_value("HD Ticket", doc.name, "_assign", "[]")
    doc._assign = []

    # 3. Create NEW ToDo for current user
    todo = frappe.get_doc({
        "doctype": "ToDo",
        "reference_type": "HD Ticket",
        "reference_name": doc.name,
        "status": "Open",
        "allocated_to": frappe.session.user,
        "description": f"Started by {frappe.session.user}",
        "priority": "Medium"
    })
    todo.insert(ignore_permissions=True)

    # 4. Update _assign
    frappe.db.set_value("HD Ticket", doc.name, "_assign", json.dumps([frappe.session.user]))
    doc._assign = [frappe.session.user]

    # 5. Ensure status flag
    if doc.status != IN_PROGRESS_STATUS:
        doc.status = IN_PROGRESS_STATUS

    frappe.db.commit()



def notify_ticket_status_change(doc, method):
    """Notify frontend on status change"""
    if doc.has_value_changed("status"):
        frappe.publish_realtime("doc_update", {
            "doctype": doc.doctype,
            "doc": doc.name,
            "status": doc.status
        }, user=frappe.session.user)


def prevent_frappe_auto_assignment(doc, method):
    """Block Frappe's built-in assignment handlers"""
    doc.flags.ignore_auto_assignment = True