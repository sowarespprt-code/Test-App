def get_receipts():
    import frappe
    res = frappe.db.sql("SELECT name, parent, receipt_date, amount_received, payment_mode, creation FROM `tabPayment Collection Receipt` WHERE parent='PCT-00005'", as_dict=True)
    for r in res:
        print(f"Receipt: {r.name}, Amount: {r.amount_received}, Mode: {r.payment_mode}, Date: {r.receipt_date}, Created: {r.creation}")
