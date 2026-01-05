# Copyright (c) 2026, soware and contributors
# For license information, please see license.txt

# import frappe


import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "label": _("Customer Code"),
            "fieldname": "customer_code",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Customer Name"),
            "fieldname": "customer_name",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("AMC End Date"),
            "fieldname": "amc_end_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": _("Address"),
            "fieldname": "address",
            "fieldtype": "Small Text",
            "width": 250
        },
        {
            "label": _("Phone"),
            "fieldname": "phone",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Product"),
            "fieldname": "product",
            "fieldtype": "Data",
            "width": 150
        }
    ]

def get_data(filters=None):
    conditions = []
    values = []
    today = frappe.utils.today()
    
    # Customer filter
    if filters and filters.get("customer_name"):
        conditions.append("customer_name = %s")
        values.append(filters.get("customer_name"))
    
    # AMC Status filter
    if filters and filters.get("amc_status") and filters.get("amc_status") != "All":
        conditions.append("custom_dateofamclastpaid IS NOT NULL")
        conditions.append("custom_dateofamclastpaid != ''")
        
        if filters.get("amc_status") == "AMC Expired":
            conditions.append("custom_dateofamclastpaid < %s")
            values.append(today)
            
        elif filters.get("amc_status") == "Upcoming Expiry":
            conditions.append("custom_dateofamclastpaid >= %s")
            values.append(today)
            
            # Month filter
            if filters.get("expiry_month"):
                month_map = {
                    "January": 1, "February": 2, "March": 3, "April": 4,
                    "May": 5, "June": 6, "July": 7, "August": 8,
                    "September": 9, "October": 10, "November": 11, "December": 12
                }
                month_num = month_map.get(filters.get("expiry_month"))
                if month_num:
                    conditions.append("MONTH(custom_dateofamclastpaid) = %s")
                    values.append(month_num)
            
            # Year filter
            if filters.get("expiry_year"):
                try:
                    year_num = int(filters.get("expiry_year"))
                    conditions.append("YEAR(custom_dateofamclastpaid) = %s")
                    values.append(year_num)
                except:
                    pass
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    query = f"""
        SELECT
            custom_customercode AS customer_code,
            customer_name,
            custom_dateofamclastpaid AS amc_end_date,
            custom_address1 AS address,
            custom_phone001 AS phone,
            custom_productname AS product
        FROM `tabHD Customer`
        {where_clause}
        ORDER BY
            custom_dateofamclastpaid ASC,
            customer_name ASC
    """
    
    data = frappe.db.sql(query, tuple(values), as_dict=True)
    return data or []










