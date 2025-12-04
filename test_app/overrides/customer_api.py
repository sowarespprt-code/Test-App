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
    Search HD Customers - ALL words must match (AND logic) like your example query.
    """
    try:
        if not search_term or len(search_term.strip()) < 1:
            return []

        # Clean and split search term into words
        search_words = [word.strip() for word in search_term.split() if len(word.strip()) > 0]
        if not search_words:
            return []

        # Build the concatenated search field exactly like your query
        concat_field = f"""
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

        # Create AND conditions for each word
        conditions = [f"({concat_field} LIKE %s)" for _ in search_words]
        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT 
                name, customer_name, custom_sl_no, custom_customercode, 
                custom_productname, custom_address1, custom_address2, 
                custom_place, custom_district, custom_phone001, custom_phone002
            FROM `tabHD Customer`
            WHERE {where_clause}
            ORDER BY modified DESC
            LIMIT 20
        """

        # Parameters: each word repeated once (for AND logic)
        params = [f"%{word}%" for word in search_words]

        customers = frappe.db.sql(query, params, as_dict=True)
        return customers

    except Exception as e:
        frappe.log_error(f"Error in search_hd_customers: {str(e)}", "Customer Search Error")
        return []


@frappe.whitelist()
def get_hd_customer_details(customer_name):
    """
    Fetch complete details of a specific HD Customer
    
    API Endpoint: /api/method/helpdesk.api.customer_api.get_hd_customer_details
    """
    try:
        if not customer_name:
            frappe.throw(_("Customer name is required"))
        
        # Check if customer exists and user has permission
        if not frappe.has_permission("HD Customer", "read", customer_name):
            frappe.throw(_("Insufficient permissions to access this customer"))
        
        # Get the complete customer document
        customer = frappe.get_doc("HD Customer", customer_name)
        
        # Return all relevant fields as dictionary
        return {
            "name": customer.name,
            "customer_name": customer.customer_name,
            "custom_sl_no": customer.custom_sl_no if hasattr(customer, 'custom_sl_no') else None,
            "custom_customercode": customer.custom_customercode if hasattr(customer, 'custom_customercode') else None,
            "custom_address1": customer.custom_address1 if hasattr(customer, 'custom_address1') else None,
            "custom_address2": customer.custom_address2 if hasattr(customer, 'custom_address2') else None,
            "custom_place": customer.custom_place if hasattr(customer, 'custom_place') else None,
            "custom_district": customer.custom_district if hasattr(customer, 'custom_district') else None,
            "custom_state": customer.custom_state if hasattr(customer, 'custom_state') else None,
            "custom_country": customer.custom_country if hasattr(customer, 'custom_country') else None,
            "custom_contactperson": customer.custom_contactperson if hasattr(customer, 'custom_contactperson') else None,
            "custom_phone001": customer.custom_phone001 if hasattr(customer, 'custom_phone001') else None,
            "custom_phone002": customer.custom_phone002 if hasattr(customer, 'custom_phone002') else None,
            "custom_gstno": customer.custom_gstno if hasattr(customer, 'custom_gstno') else None,
            "custom_email": customer.custom_email if hasattr(customer, 'custom_email') else None,
            "custom_productname": customer.custom_productname if hasattr(customer, 'custom_productname') else None,
            "custom_nooflicense": customer.custom_nooflicense if hasattr(customer, 'custom_nooflicense') else None,
            "custom_dateofamclastpaid": customer.custom_dateofamclastpaid if hasattr(customer, 'custom_dateofamclastpaid') else None,
        }
        
    except frappe.DoesNotExistError:
        frappe.throw(_("Customer not found"))
    except frappe.PermissionError:
        frappe.throw(_("You don't have permission to access this customer"))
    except Exception as e:
        frappe.log_error(f"Error in get_hd_customer_details: {str(e)}", "Customer Details Error")
        frappe.throw(_("Error fetching customer details. Please try again."))