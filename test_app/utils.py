import json
import frappe
from frappe.desk.form.assign_to import add as add_assignment 

NOT_ASSIGNED_STATUS = "Not Assigned"  # put your exact status text here

def auto_assign_on_status_change(doc, method):
    # only for existing tickets; for new ones you can decide separately
    if doc.is_new():
        return

    # previous version of the document
    old = doc.get_doc_before_save()
    if not old:
        return

    # 🔴 FORCE CLEAR ASSIGNEES when status goes BACK to Not Assigned
    if old.status != NOT_ASSIGNED_STATUS and doc.status == NOT_ASSIGNED_STATUS:

        # 1️⃣ Cancel existing ToDo assignments properly
        todos = frappe.get_all(
            "ToDo",
            filters={
                "reference_type": doc.doctype,
                "reference_name": doc.name,
                "status": ["!=", "Cancelled"],
            },
            pluck="name",
        )

        for todo in todos:
            frappe.db.set_value("ToDo", todo, "status", "Cancelled")

        # 2️⃣ Clear assignment cache (_assign)
        doc._assign = None
        frappe.db.set_value(doc.doctype, doc.name, "_assign", None)

        # 3️⃣ Ensure no reassignment happens in same save
        frappe.db.commit()
        return

    # status changed from Not Assigned to something else
    if old.status == NOT_ASSIGNED_STATUS and doc.status != NOT_ASSIGNED_STATUS:
        # skip Administrator
        if frappe.session.user == "Administrator":
            return

        # check if there is already an assignment
        existing_assignments = frappe.get_all(
            "ToDo",
            filters={
                "reference_type": doc.doctype,
                "reference_name": doc.name,
                "status": ["!=", "Cancelled"],
            },
            limit=1,
        )[0:1]

        if existing_assignments:
            return  # someone already assigned, don’t override

        # create assignment for the current user
        add_assignment(
            {
                "doctype": doc.doctype,
                "name": doc.name,
                "assign_to": [frappe.session.user],
                "description": f"Auto-assigned on status change to {doc.status}",
            }
        )


def clear_ticket_todo_on_unassign(doc, method):
    """Auto-delete ToDo when all assignments are cleared"""
    # Only run when _assign field changes
    if not doc.has_value_changed("_assign"):
        return

    # _assign is a JSON list of user ids (or empty string)
    assign_raw = doc.get("_assign") or "[]"
    try:
        assigned_users = json.loads(assign_raw)
    except Exception:
        assigned_users = []

    # If no assigned users → clear ToDos
    if not assigned_users:
        todos = frappe.get_all(
            "ToDo",
            filters={
                "reference_type": "HD Ticket",
                "reference_name": doc.name,
                "status": "Open",
            },
        )
        for t in todos:
            frappe.delete_doc("ToDo", t.name, force=True, ignore_permissions=True)

        frappe.db.commit()


def notify_ticket_status_change(doc, method):
    """Notify frontend on status change"""
    if doc.has_value_changed("status"):
        frappe.publish_realtime("doc_update", {
            "doctype": doc.doctype,
            "doc": doc.name,
            "status": doc.status
        }, user=frappe.session.user)



