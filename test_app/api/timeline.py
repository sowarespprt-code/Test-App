import frappe
from frappe.utils import get_fullname
from helpdesk.helpdesk.doctype.hd_ticket.api import get_user_info_for_avatar, get_attachments

@frappe.whitelist()
def get_task_activities(doctype: str, docname: str):
    if not frappe.has_permission(doctype, "read", docname):
        frappe.throw(f"Not permitted to view {doctype}", frappe.PermissionError)
        
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
            
            if "changed" in data and len(data["changed"]) > 0:
                for change in data["changed"]:
                    field = frappe.get_meta(doctype).get_field(change[0])
                    label = field.label if field else change[0]
                    history.append({
                        "name": v.name,
                        "action": f"set {label} to {change[2]}",
                        "owner": v.owner,
                        "creation": v.creation,
                        "user": get_user_info_for_avatar(v.owner)
                    })

            if "row_changed" in data:
                # In newer Frappe versions, row_changed is a list of lists:
                # [[table_fieldname, row_idx, row_name, [[fieldname, old_value, new_value], ...]], ...]
                row_changes_data = data["row_changed"]
                
                if isinstance(row_changes_data, dict):
                    # fallback for older frappe
                    for table_name, rows in row_changes_data.items():
                        field = frappe.get_meta(doctype).get_field(table_name)
                        table_label = field.label if field else table_name
                        child_doctype = field.options if field else None
                        
                        for row in rows:
                            row_changes = row[1]
                            for field_name, vals in row_changes.items():
                                field_label = field_name
                                if child_doctype:
                                    cfield = frappe.get_meta(child_doctype).get_field(field_name)
                                    if cfield:
                                        field_label = cfield.label
                                        
                                history.append({
                                    "name": v.name,
                                    "action": f"updated {field_label} to {vals[1]} in {table_label}",
                                    "owner": v.owner,
                                    "creation": v.creation,
                                    "user": get_user_info_for_avatar(v.owner)
                                })
                elif isinstance(row_changes_data, list):
                    for row_change in row_changes_data:
                        if len(row_change) < 4: continue
                        table_name = row_change[0]
                        field = frappe.get_meta(doctype).get_field(table_name)
                        table_label = field.label if field else table_name
                        child_doctype = field.options if field else None
                        
                        field_changes = row_change[3]
                        for change in field_changes:
                            field_name = change[0]
                            new_val = change[2]
                            
                            field_label = field_name
                            if child_doctype:
                                cfield = frappe.get_meta(child_doctype).get_field(field_name)
                                if cfield:
                                    field_label = cfield.label
                            
                            history.append({
                                "name": v.name,
                                "action": f"updated {field_label} to {new_val} in {table_label}",
                                "owner": v.owner,
                                "creation": v.creation,
                                "user": get_user_info_for_avatar(v.owner)
                            })
                            
            if "added" in data:
                for row in data["added"]:
                    if not isinstance(row, list) or len(row) == 0:
                        continue
                    table_name = row[0]
                    if table_name in ["call_history", "payment_commitments", "payment_receipts"]:
                        continue
                    field = frappe.get_meta(doctype).get_field(table_name)
                    table_label = field.label if field else table_name
                    history.append({
                        "name": v.name,
                        "action": f"added a row to {table_label}",
                        "owner": v.owner,
                        "creation": v.creation,
                        "user": get_user_info_for_avatar(v.owner)
                    })
                    
            if "removed" in data:
                for row in data["removed"]:
                    if not isinstance(row, list) or len(row) == 0:
                        continue
                    table_name = row[0]
                    if table_name in ["call_history", "payment_commitments", "payment_receipts"]:
                        continue
                    field = frappe.get_meta(doctype).get_field(table_name)
                    table_label = field.label if field else table_name
                    history.append({
                        "name": v.name,
                        "action": f"removed a row from {table_label}",
                        "owner": v.owner,
                        "creation": v.creation,
                        "user": get_user_info_for_avatar(v.owner)
                    })
        except Exception as e:
            import traceback
            frappe.log_error(f"Error parsing version {v.name}\n{traceback.format_exc()}")
            pass
            
    # Add creation event
    doc_meta = frappe.db.get_value(doctype, docname, ["owner", "creation"], as_dict=True)
    if doc_meta:
        history.append({
            "name": f"creation_{docname}",
            "action": "created this",
            "owner": doc_meta.owner,
            "creation": doc_meta.creation,
            "user": get_user_info_for_avatar(doc_meta.owner)
        })
        
    if doctype == "Payment Collection Task":
        doc = frappe.get_doc(doctype, docname)
        for call in doc.get("call_history", []):
            history.append({
                "name": f"call_{call.name}",
                "action": f"logged a call. Summary: '{call.discussion_summary}'. Outcome: {call.call_outcome or 'N/A'}",
                "owner": call.owner,
                "creation": call.creation,
                "user": get_user_info_for_avatar(call.owner)
            })
            
        for comm in doc.get("payment_commitments", []):
            history.append({
                "name": f"comm_{comm.name}",
                "action": f"created a payment commitment for {frappe.utils.fmt_money(comm.promised_amount, currency='INR')} due on {frappe.utils.formatdate(comm.promised_payment_date)}",
                "owner": comm.owner,
                "creation": comm.creation,
                "user": get_user_info_for_avatar(comm.owner)
            })
            
        for rec in doc.get("payment_receipts", []):
            history.append({
                "name": f"rec_{rec.name}",
                "action": f"added a payment receipt of {frappe.utils.fmt_money(rec.amount_received or 0, currency='INR')} via {rec.payment_mode or 'Unknown'}",
                "owner": rec.owner,
                "creation": rec.creation,
                "user": get_user_info_for_avatar(rec.owner)
            })
            
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
