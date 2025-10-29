import frappe

@frappe.whitelist()
def get_customer_details(customer):
    """Get customer details with all custom fields"""
    
    if not customer:
        return {}
    
    # Get the customer document
    customer_doc = frappe.get_doc('HD Customer', customer)
    
    # Get all fields from meta
    meta = frappe.get_meta('HD Customer')
    
    # Build response with all field values
    result = {
        'name': customer_doc.name,
        'fields': []
    }
    
    for field in meta.fields:
        # Skip system fields
        if field.fieldname in ['amended_from', 'naming_series', 'docstatus']:
            continue
            
        if field.hidden:
            continue
        
        result['fields'].append({
            'fieldname': field.fieldname,
            'label': field.label,
            'fieldtype': field.fieldtype,
            'value': customer_doc.get(field.fieldname),
            'options': field.options
        })
    
    return result