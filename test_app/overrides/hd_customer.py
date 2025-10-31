import frappe
from frappe.model.document import Document


class HDCustomer(Document):
    def validate(self):
        """This ALWAYS runs before any save (edit, create, update, etc)"""
        frappe.log_error("Validate method executed", "HD Customer - Validate")

        # Find tickets for this customer
        tickets = frappe.db.get_all(
            'HD Ticket',
            filters={'custom_customer_name': self.name},
            fields=['name']
        )

        frappe.log_error(f"Found {len(tickets)} tickets for customer {self.name}", "HD Customer - Tickets Found (Validate)")

        if not tickets:
            return

        # Update all tickets
        for ticket in tickets:
            frappe.db.set_value(
                'HD Ticket',
                ticket.name,
                {
                    'custom_customercode': self.custom_customercode or '',
                    'custom_product': self.custom_productname or ''
                },
                update_modified=True
            )

        frappe.db.commit()

        frappe.msgprint(
            f'Updated {len(tickets)} ticket(s)',
            title='Tickets Synced',
            indicator='green',
            alert=True
        )

    @staticmethod
    def default_list_data():
        columns = [
            {
                "label": "Name",
                "key": "name",
                "width": "17rem",
                "type": "Data",
            },
            {
                "label": "Domain",
                "key": "domain",
                "width": "24rem",
                "type": "Data",
            },
            {
                "label": "Created On",
                "key": "creation",
                "width": "8rem",
                "type": "Datetime",
            },
        ]
        return {"columns": columns}
