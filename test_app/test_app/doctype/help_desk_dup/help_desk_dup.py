# Copyright (c) 2026, soware and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Helpdeskdup(Document):
	pass

from frappe.model.mapper import get_mapped_doc

def hd_to_hdd(self, method = None):
	doc = make_test_from_hd_ticket(self.name)
	doc.insert(ignore_permissions = True)
	frappe.db.commit()


@frappe.whitelist()
def make_test_from_hd_ticket(source_name, target_doc=None):
	doc = get_mapped_doc(
		"HD Ticket",   # source doctype (confirm exact name)
		source_name,
		{
			"HD Ticket": {
				"doctype": "Help desk dup",
				"field_map": {}
			}
		},
		target_doc
	)

	return doc
