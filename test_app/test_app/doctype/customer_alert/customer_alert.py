# Copyright (c) 2025, soware and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CustomerAlert(Document):
	@frappe.whitelist()
	def get_customer_alert(customer_name):
		"""Get existing customer alert if it exists for the HD Customer"""
		
		if not customer_name:
			return None
		
		existing = frappe.get_all(
			'Customer Alert',
			filters={'customer_name': customer_name},
			fields=['name', 'customer_name', 'remarks'],
			limit=1
		)
		
		if existing:
			return frappe.get_doc('Customer Alert', existing[0].name)
		
		return None


	@frappe.whitelist()
	def create_or_update_customer_alert(customer_name, remarks, name=None):
		"""Create new or update existing customer alert"""
		
		if not customer_name:
			frappe.throw(_('HD Customer is required'))
		
		# Check if document already exists
		if name:
			doc = frappe.get_doc('Customer Alert', name)
		else:
			existing = frappe.get_all(
				'Customer Alert',
				filters={'customer_name': customer_name},
				fields=['name'],
				limit=1
			)
			
			if existing:
				# Update existing document
				doc = frappe.get_doc('Customer Alert', existing[0].name)
			else:
				# Create new document
				doc = frappe.new_doc('Customer Alert')
				doc.customer_name = customer_name
		
		doc.remarks = remarks
		doc.save()
		
		frappe.msgprint(
			_('Customer Alert for {0} has been saved successfully').format(frappe.bold(customer_name)),
			title=_('Success'),
			indicator='green'
		)
		
		return doc