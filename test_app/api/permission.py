import frappe

def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return ""
        
    roles = frappe.get_roles(user)
    if "System Manager" in roles or "Agent Manager" in roles:
        return ""
        
    # For regular users (assignees), they can see all tasks as requested by the user
    return ""

def has_permission(doc, user=None, permission_type="read"):
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return True
        
    roles = frappe.get_roles(user)
    if "System Manager" in roles or "Agent Manager" in roles:
        return True
        
    return True
