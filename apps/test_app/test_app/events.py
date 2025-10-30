import frappe

def custom_field_updated(doc, method):
    """
    Automatically clear cache and reload metadata when a Custom Field is
    added, edited, or deleted for HD Customer.
    """
    try:
        # Only handle HD Customer fields
        if doc.dt == "HD Customer":
            frappe.clear_cache(doctype="HD Customer")
            frappe.msgprint("HD Customer fields updated and cache cleared. Changes will reflect automatically.")
    except Exception as e:
        frappe.log_error(f"Custom field update handler failed: {e}")
