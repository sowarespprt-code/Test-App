import json

path = '/home/user/test-bench/apps/test_app/test_app/fixtures/server_script.json'
with open(path, 'r') as f:
    scripts = json.load(f)

for script in scripts:
    if script.get('name') == 'To Fill customer Name' and script.get('reference_doctype') == 'HD Ticket':
        script['script'] = """customer_code = (doc.custom_customercode or "").strip()

if customer_code:
    customer = frappe.db.get_value(
        "HD Customer",
        {"custom_customercode": customer_code},
        ["name", "customer_name", "custom_contactperson", "custom_phone001"],
        as_dict=True
    )

    if customer:
        doc.customer = customer.name
        doc.custom_customer_name = customer.customer_name
        if customer.custom_contactperson:
            doc.custom_contactperson = customer.custom_contactperson
        if customer.custom_phone001:
            doc.custom_phone_number = customer.custom_phone001
    else:
        frappe.throw(f"HD Customer not found for Customer Code: {customer_code}")
"""
        break

with open(path, 'w') as f:
    json.dump(scripts, f, indent=1)
print("Updated server script")
