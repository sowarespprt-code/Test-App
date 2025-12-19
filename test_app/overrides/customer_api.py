"""
Custom API for HD Customer Search
Location: test_app/test_app/overrides/customer_api.py
Will be copied to: helpdesk/api/customer_api.py
"""

import frappe
from frappe import _


@frappe.whitelist()
def search_hd_customers(search_term):
    """
    Search HD Customers.
    - All words in search_term must match (AND logic).
    - Only customers with status = 'Enabled' are returned.
    """
    try:
        if not search_term or len(search_term.strip()) < 1:
            return []

        # Clean and split search term into words
        search_words = [
            word.strip()
            for word in search_term.split()
            if len(word.strip()) > 0
        ]
        if not search_words:
            return []

        # Build the concatenated search field
        concat_field = """
            CONCAT(
                custom_customercode, ' ',
                customer_name, ' ',
                IFNULL(custom_address1, ''), ' ',
                IFNULL(custom_address2, ''), ' ',
                IFNULL(custom_place, ''), ' ',
                IFNULL(custom_phone001, ''), ' ',
                IFNULL(custom_phone002, '')
            )
        """

        # One LIKE condition per word, combined with AND
        conditions = [f"({concat_field} LIKE %s)" for _ in search_words]
        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT
                name,
                customer_name,
                custom_sl_no,
                custom_customercode,
                custom_productname,
                custom_address1,
                custom_address2,
                custom_place,
                custom_district,
                custom_phone001,
                custom_phone002
            FROM `tabHD Customer`
            WHERE custom_status = 'Enabled'
              AND {where_clause}
            ORDER BY modified DESC
            LIMIT 20
        """

        params = [f"%{word}%" for word in search_words]

        customers = frappe.db.sql(query, params, as_dict=True)
        return customers

    except Exception as e:
        frappe.log_error(
            f"Error in search_hd_customers: {str(e)}",
            "Customer Search Error",
        )
        return []


@frappe.whitelist()
def get_hd_customer_details(customer_name):
    """
    Fetch complete details of a specific HD Customer.

    Only returns data if:
    - customer exists
    - user has read permission
    - customer.status == 'Enabled'
    """
    try:
        if not customer_name:
            frappe.throw(_("Customer name is required"))

        if not frappe.has_permission("HD Customer", "read", customer_name):
            frappe.throw(_("Insufficient permissions to access this customer"))

        customer = frappe.get_doc("HD Customer", customer_name)

        # Enforce only Enabled customers
        if getattr(customer, "status", None) != "Enabled":
            frappe.throw(_("Customer is disabled and cannot be selected"))

        return {
            "name": customer.name,
            "customer_name": customer.customer_name,
            "custom_sl_no": getattr(customer, "custom_sl_no", None),
            "custom_customercode": getattr(customer, "custom_customercode", None),
            "custom_address1": getattr(customer, "custom_address1", None),
            "custom_address2": getattr(customer, "custom_address2", None),
            "custom_place": getattr(customer, "custom_place", None),
            "custom_district": getattr(customer, "custom_district", None),
            "custom_state": getattr(customer, "custom_state", None),
            "custom_country": getattr(customer, "custom_country", None),
            "custom_contactperson": getattr(customer, "custom_contactperson", None),
            "custom_phone001": getattr(customer, "custom_phone001", None),
            "custom_phone002": getattr(customer, "custom_phone002", None),
            "custom_gstno": getattr(customer, "custom_gstno", None),
            "custom_email": getattr(customer, "custom_email", None),
            "custom_productname": getattr(customer, "custom_productname", None),
            "custom_nooflicense": getattr(customer, "custom_nooflicense", None),
            "custom_dateofamclastpaid": getattr(customer, "custom_dateofamclastpaid", None
            ),
        }

    except frappe.DoesNotExistError:
        frappe.throw(_("Customer not found"))
    except frappe.PermissionError:
        frappe.throw(_("You don't have permission to access this customer"))
    except Exception as e:
        frappe.log_error(
            f"Error in get_hd_customer_details: {str(e)}",
            "Customer Details Error",
        )
        frappe.throw(_("Error fetching customer details. Please try again."))