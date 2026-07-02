import frappe
from frappe.utils import get_fullname
from helpdesk.helpdesk.doctype.hd_ticket.api import get_user_info_for_avatar, get_attachments

@frappe.whitelist()
def get_task_activities(doctype: str, docname: str):
    activities = {
        "comments": get_comments(doctype, docname),
        "history": get_history(doctype, docname),
        "views": get_views(doctype, docname),
        "communications": [],
        "calls": []
    }
    return activities

def get_comments(doctype: str, docname: str):
    if not frappe.has_permission("Comment", "read"):
        return []
    QBComment = frappe.qb.DocType("Comment")
    comments = (
        frappe.qb.from_(QBComment)
        .select(
            QBComment.owner.as_("commented_by"),
            QBComment.content,
            QBComment.creation,
            QBComment.name,
        )
        .where(QBComment.reference_doctype == doctype)
        .where(QBComment.reference_name == docname)
        .orderby(QBComment.creation)
        .run(as_dict=True)
    )
    for c in comments:
        c.user = get_user_info_for_avatar(c.commented_by)
        c.attachments = [] # Comments attachment could be fetched if needed
    return comments

def get_history(doctype: str, docname: str):
    if not frappe.has_permission("Version", "read"):
        return []
    QBVersion = frappe.qb.DocType("Version")
    versions = (
        frappe.qb.from_(QBVersion)
        .select(QBVersion.name, QBVersion.data, QBVersion.owner, QBVersion.creation)
        .where(QBVersion.ref_doctype == doctype)
        .where(QBVersion.docname == docname)
        .orderby(QBVersion.creation, order=frappe.qb.desc)
        .run(as_dict=True)
    )
    history = []
    import json
    for v in versions:
        try:
            data = json.loads(v.data)
            action = "changed something"
            if "changed" in data and len(data["changed"]) > 0:
                changes = []
                for change in data["changed"]:
                    field = frappe.get_meta(doctype).get_field(change[0])
                    label = field.label if field else change[0]
                    changes.append(f"set {label} to {change[2]}")
                action = ", ".join(changes)
            elif "added" in data:
                added_tables = []
                for row in data["added"]:
                    if not isinstance(row, list) or len(row) == 0:
                        continue
                    table_name = row[0]
                    if table_name == "call_history":
                        added_tables.append("a Call Log")
                    elif table_name == "payment_commitments":
                        added_tables.append("a Payment Commitment")
                    elif table_name == "payment_receipts":
                        added_tables.append("a Receipt")
                    else:
                        label = frappe.get_meta(doctype).get_field(table_name).label if frappe.get_meta(doctype).get_field(table_name) else table_name
                        added_tables.append(f"a {label}")
                if added_tables:
                    # Remove duplicates and join
                    action = f"added {', '.join(list(dict.fromkeys(added_tables)))}"
                else:
                    action = "added a row"
            elif "removed" in data:
                action = "removed row"
            
            history.append({
                "name": v.name,
                "action": action,
                "owner": v.owner,
                "creation": v.creation,
                "user": get_user_info_for_avatar(v.owner)
            })
        except:
            pass
    return history

def get_views(doctype: str, docname: str):
    QBViewLog = frappe.qb.DocType("View Log")
    views = (
        frappe.qb.from_(QBViewLog)
        .select(QBViewLog.name, QBViewLog.owner, QBViewLog.creation)
        .where(QBViewLog.reference_doctype == doctype)
        .where(QBViewLog.reference_name == docname)
        .orderby(QBViewLog.creation, order=frappe.qb.desc)
        .run(as_dict=True)
    )
    for v in views:
        v.user = get_user_info_for_avatar(v.owner)
    return views


@frappe.whitelist()
def log_view(doctype: str, docname: str):
    try:
        doc = frappe.get_doc(doctype, docname)
        
        # Don't use unique_views=True so that every view gets logged separately
        doc.add_viewed(unique_views=False, force=True)
    except Exception:
        pass
