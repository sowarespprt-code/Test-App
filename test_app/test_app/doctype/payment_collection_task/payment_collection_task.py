import frappe
from frappe.model.document import Document

class PaymentCollectionTask(Document):
	def validate(self):
		# 1. Calculate Collected Amount from receipts child table
		collected = 0.0
		if self.payment_receipts:
			for receipt in self.payment_receipts:
				collected += float(receipt.amount_received or 0.0)
		self.collected_amount = collected

		# 2. Calculate Outstanding Amount
		total_due = float(self.payment_amount or 0.0)
		self.outstanding_amount = max(0.0, total_due - self.collected_amount)


		# 4. Status validation
		# Auto-transition back from Completed if amount is edited
		if self.status == "Completed" and self.outstanding_amount > 0.0:
			if not self.is_new() and getattr(self, "flags", {}).get("is_api_update"):
				self.status = "Partially Paid" if self.collected_amount > 0.0 else "Open"
			else:
				# If not from API, we still revert it to avoid breaking when amounts change
				self.status = "Partially Paid" if self.collected_amount > 0.0 else "Open"

		# Auto-transition Open/In Progress status to Partially Paid if payment is received but outstanding exists
		if self.collected_amount > 0.0 and frappe.utils.flt(self.outstanding_amount) > 0.0:
			if self.status in ["Open", "In Progress"]:
				self.status = "Partially Paid"
				
		# Auto-transition to Completed if fully paid
		if self.collected_amount > 0.0 and frappe.utils.flt(self.outstanding_amount) <= 0.0:
			if self.status != "Completed":
				self.status = "Completed"
