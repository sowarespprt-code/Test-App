import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
    # Update status options
    doc = frappe.get_doc("DocType", "Payment Collection Commitment")
    status_field = next(f for f in doc.fields if f.fieldname == "status")
    if "Partially Paid" not in status_field.options:
        status_field.options = status_field.options.replace("Received", "Received\nPartially Paid")
        doc.save()

    # Add custom fields if they don't exist
    create_custom_field("Payment Collection Commitment", {
        "fieldname": "amount_paid",
        "label": "Amount Paid",
        "fieldtype": "Currency",
        "insert_after": "promised_amount"
    })
    create_custom_field("Payment Collection Commitment", {
        "fieldname": "next_follow_up_date",
        "label": "Next Follow-up Date",
        "fieldtype": "Date",
        "insert_after": "status"
    })
    create_custom_field("Payment Collection Commitment", {
        "fieldname": "customer_remarks",
        "label": "Customer Remarks",
        "fieldtype": "Small Text",
        "insert_after": "next_follow_up_date"
    })
    
    frappe.db.commit()
    print("Schema updated successfully")
