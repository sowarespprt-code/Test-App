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

		# 3. Auto-update Next Follow-up Date from the latest call in Call History
		self.next_follow_up_date = None
		if self.call_history:
			# Sort calls by call date/time descending to get the latest call
			sorted_calls = sorted(
				self.call_history,
				key=lambda x: x.call_date_and_time or "",
				reverse=True
			)
			for call in sorted_calls:
				if call.next_follow_up_date:
					self.next_follow_up_date = call.next_follow_up_date
					break

		# 4. Status validation
		# Prevent marking as Completed if there is still outstanding balance
		if self.status == "Completed" and self.outstanding_amount > 0.0:
			frappe.throw(
				f"Cannot mark task as Completed because there is an outstanding balance of "
				f"{frappe.utils.fmt_money(self.outstanding_amount)}"
			)

		# Auto-transition Open/In Progress status to Partially Paid if payment is received but outstanding exists
		if self.collected_amount > 0.0 and self.outstanding_amount > 0.0:
			if self.status in ["Open", "In Progress"]:
				self.status = "Partially Paid"
				frappe.msgprint("Status updated to 'Partially Paid' as payment is received.")
