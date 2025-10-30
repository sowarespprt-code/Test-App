import frappe

@frappe.whitelist()
def get_teams():
    """Get list of all HD Teams"""
    try:
        teams = frappe.get_all(
            "HD Team",
            fields=["name"],
            order_by="name asc"
        )
        return teams
    except Exception as e:
        frappe.log_error(f"Error fetching teams: {str(e)}")
        return []

@frappe.whitelist()
def get_product_details(product_name):
    """Get product details with team info"""
    try:
        product = frappe.get_doc("Product", product_name)
        return product.as_dict()
    except Exception as e:
        frappe.throw(f"Error fetching product: {str(e)}")