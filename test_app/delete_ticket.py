import frappe
def run():
    ticket = frappe.get_all("HD Ticket", limit=1)
    if not ticket:
        print("No tickets found")
        return
    ticket_name = ticket[0].name
    print(f"Deleting {ticket_name}")
    try:
        frappe.delete_doc("HD Ticket", ticket_name)
        frappe.db.commit()
        print("Deleted successfully")
    except Exception as e:
        import traceback
        traceback.print_exc()
