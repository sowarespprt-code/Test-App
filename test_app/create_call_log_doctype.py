import frappe

def create_doctype():
    if not frappe.db.exists("DocType", "Call Management Log"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Call Management Log",
            "module": "test_app",
            "custom": 0,
            "istable": 0,
            "fields": [
                {"fieldname": "payment_collection_task", "fieldtype": "Link", "options": "Payment Collection Task", "label": "Payment Collection Task"},
                {"fieldname": "call_date_and_time", "fieldtype": "Datetime", "label": "Call Date and Time"},
                {"fieldname": "staff_member", "fieldtype": "Link", "options": "User", "label": "Staff Member"},
                {"fieldname": "customer_response", "fieldtype": "Select", "options": "\nPositive\nNegative\nNeutral\nNo Answer\nBusy\nWrong Number\nDisconnected", "label": "Customer Response"},
                {"fieldname": "call_outcome", "fieldtype": "Select", "options": "\nPromise to Pay\nRefusal to Pay\nDispute\nRequest for Time\nLeft Message\nCall Back Required\nEscalated", "label": "Call Outcome"},
                {"fieldname": "discussion_summary", "fieldtype": "Small Text", "label": "Discussion Summary"},
                {"fieldname": "promised_amount", "fieldtype": "Currency", "label": "Promised Amount"},
                {"fieldname": "promised_payment_date", "fieldtype": "Date", "label": "Promised Payment Date"},
                {"fieldname": "next_follow_up_date", "fieldtype": "Date", "label": "Next Follow-up Date"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print("Created Call Management Log Doctype")
        frappe.db.commit()
    else:
        print("Call Management Log Doctype already exists")
