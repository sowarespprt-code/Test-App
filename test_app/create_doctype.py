import frappe

def create_call_management_log_doctype():
    if frappe.db.exists("DocType", "Call Management Log"):
        print("Call Management Log Doctype already exists.")
        return

    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": "Call Management Log",
        "module": "Test App",
        "custom": 1,
        "is_submittable": 0,
        "fields": [
            {
                "fieldname": "payment_collection_task",
                "label": "Payment Collection Task",
                "fieldtype": "Link",
                "options": "Payment Collection Task",
                "reqd": 1,
                "in_list_view": 1
            },
            {
                "fieldname": "call_date_and_time",
                "label": "Call Date and Time",
                "fieldtype": "Datetime",
                "reqd": 1,
                "in_list_view": 1
            },
            {
                "fieldname": "staff_member",
                "label": "Staff Member",
                "fieldtype": "Link",
                "options": "User",
                "reqd": 1
            },
            {
                "fieldname": "customer_response",
                "label": "Customer Response",
                "fieldtype": "Data",
                "reqd": 1
            },
            {
                "fieldname": "call_outcome",
                "label": "Call Outcome",
                "fieldtype": "Data"
            },
            {
                "fieldname": "discussion_summary",
                "label": "Discussion Summary",
                "fieldtype": "Small Text"
            },
            {
                "fieldname": "promised_amount",
                "label": "Promised Amount",
                "fieldtype": "Currency"
            },
            {
                "fieldname": "promised_payment_date",
                "label": "Promised Payment Date",
                "fieldtype": "Date"
            },
            {
                "fieldname": "next_follow_up_date",
                "label": "Next Follow Up Date",
                "fieldtype": "Date"
            }
        ],
        "permissions": [
            {
                "role": "System Manager",
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1
            },
            {
                "role": "Desk User",
                "read": 1,
                "write": 1,
                "create": 1
            }
        ],
        "autoname": "format:CML-{####}"
    })
    doc.insert()
    print("Created Call Management Log Doctype successfully.")

if __name__ == "__main__":
    create_call_management_log_doctype()
    frappe.db.commit()
