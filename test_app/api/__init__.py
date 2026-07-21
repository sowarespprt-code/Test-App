import frappe

@frappe.whitelist()
def get_teams():
    """Get list of all HD Teams"""
    try:
        teams = frappe.get_all(
            "HD Team",
            fields=["name"],
            order_by="name asc"
        )
        return teams
    except Exception as e:
        frappe.log_error(f"Error fetching teams: {str(e)}")
        return []

@frappe.whitelist()
def get_product_details(product_name):
    """Get product details with team info"""
    try:
        product = frappe.get_doc("Product", product_name)
        return product.as_dict()
    except Exception as e:
        frappe.throw(f"Error fetching product: {str(e)}")

@frappe.whitelist()
def get_payment_dashboard_metrics():
    """Get dashboard metrics for Payment Collection module"""
    try:
        import datetime
        from frappe.utils import getdate

        user = frappe.session.user
        is_admin = "System Manager" in frappe.get_roles(user) or user == "Administrator"

        today_dt = datetime.date.today()
        today = today_dt.isoformat()
        start_of_month = today_dt.replace(day=1).isoformat()

        cond = ""
        t_cond = ""
        r_cond = ""
        params_outstanding = []
        params_collected = [start_of_month]
        params_failed = [today]
        params_staff = []

        if not is_admin:
            pass
        # 1. Total Outstanding Amount
        total_outstanding = frappe.db.sql(f"""
            SELECT SUM(outstanding_amount) 
            FROM `tabPayment Collection Task` 
            WHERE status NOT IN ('Completed', 'Cancelled') {cond}
        """, tuple(params_outstanding))[0][0] or 0.0

        # 2. Total Collected This Month
        total_collected_month = frappe.db.sql(f"""
            SELECT SUM(r.amount_received) 
            FROM `tabPayment Collection Receipt` r
            JOIN `tabPayment Collection Task` t ON r.parent = t.name
            WHERE r.receipt_date >= %s AND r.parenttype = 'Payment Collection Task' {t_cond}
        """, tuple(params_collected))[0][0] or 0.0

        # 3. Open Collection Tasks
        open_filters = {"status": ["not in", ["Completed", "Cancelled"]]}
        open_tasks = frappe.db.count("Payment Collection Task", open_filters)

        # 4. Overdue Follow-ups
        overdue_filters = {"status": ["not in", ["Completed", "Cancelled"]], "next_follow_up_date": ["<", today]}
        overdue_follow_ups = frappe.db.count("Payment Collection Task", overdue_filters)

        # 5. Pending Commitments
        pending_commitments = frappe.db.sql(f"""
            SELECT COUNT(*) 
            FROM `tabPayment Collection Commitment` c
            JOIN `tabPayment Collection Task` t ON c.parent = t.name
            WHERE c.status = 'Pending' AND c.parenttype = 'Payment Collection Task' {t_cond}
        """, tuple(params_outstanding))[0][0] or 0

        # 6. Failed Commitments
        failed_commitments = frappe.db.sql(f"""
            SELECT COUNT(*) 
            FROM `tabPayment Collection Commitment` c
            JOIN `tabPayment Collection Task` t ON c.parent = t.name
            WHERE c.parenttype = 'Payment Collection Task'
              AND (c.status = 'Not Received' OR (c.status = 'Pending' AND c.promised_payment_date < %s))
            {t_cond}
        """, tuple(params_failed))[0][0] or 0

        # 7. Staff-wise Collection Performance
        staff_performance = frappe.db.sql(f"""
            SELECT r.received_by as staff, u.full_name as staff_name, SUM(r.amount_received) as collected 
            FROM `tabPayment Collection Receipt` r
            LEFT JOIN `tabUser` u ON r.received_by = u.name
            WHERE r.parenttype = 'Payment Collection Task' {r_cond}
            GROUP BY r.received_by
            ORDER BY collected DESC
        """, tuple(params_staff), as_dict=True)

        # 8. Customer-wise Outstanding Amount
        customer_outstanding = frappe.db.sql(f"""
            SELECT t.customer as customer_name, c.customer_name as customer_display, SUM(t.outstanding_amount) as outstanding
            FROM `tabPayment Collection Task` t
            LEFT JOIN `tabHD Customer` c ON t.customer = c.name
            WHERE t.status NOT IN ('Completed', 'Cancelled') {t_cond}
            GROUP BY t.customer
            ORDER BY outstanding DESC
        """, tuple(params_outstanding), as_dict=True)

        # 9. Reminders Lists
        daily_filters = {"status": ["not in", ["Completed", "Cancelled"]], "next_follow_up_date": today}
        daily_reminders_list = frappe.db.get_list("Payment Collection Task",
            filters=daily_filters,
            fields=["name", "customer", "payment_amount", "outstanding_amount", "assigned_to", "priority", "status"]
        )

        overdue_rem_filters = {"status": ["not in", ["Completed", "Cancelled"]], "next_follow_up_date": ["<", today]}
        overdue_reminders_list = frappe.db.get_list("Payment Collection Task",
            filters=overdue_rem_filters,
            fields=["name", "customer", "payment_amount", "outstanding_amount", "assigned_to", "priority", "status", "next_follow_up_date"]
        )

        upcoming_filters = {"status": ["not in", ["Completed", "Cancelled"]], "next_follow_up_date": [">", today]}
        upcoming_follow_ups_list = frappe.db.get_list("Payment Collection Task",
            filters=upcoming_filters,
            fields=["name", "customer", "payment_amount", "outstanding_amount", "assigned_to", "priority", "status", "next_follow_up_date"]
        )

        # Map users and customers to show full name/display names in lists
        users = {u.name: u.full_name for u in frappe.get_all("User", fields=["name", "full_name"])}
        hd_customers = {c.name: c.customer_name for c in frappe.get_all("HD Customer", fields=["name", "customer_name"])}

        def enrich_list(lst):
            for item in lst:
                item["assigned_to_name"] = users.get(item.assigned_to) or item.assigned_to
                item["customer_name_display"] = hd_customers.get(item.customer) or item.customer
            return lst

        return {
            "total_outstanding_amount": total_outstanding,
            "total_collected_this_month": total_collected_month,
            "open_collection_tasks": open_tasks,
            "overdue_follow_ups": overdue_follow_ups,
            "pending_commitments": pending_commitments,
            "failed_commitments": failed_commitments,
            "staff_performance": staff_performance,
            "customer_outstanding": customer_outstanding,
            "daily_reminders": enrich_list(daily_reminders_list),
            "overdue_reminders": enrich_list(overdue_reminders_list),
            "upcoming_follow_ups": enrich_list(upcoming_follow_ups_list)
        }
    except Exception as e:
        frappe.log_error(f"Error fetching dashboard metrics: {str(e)}")
        frappe.throw(f"Error fetching dashboard metrics: {str(e)}")

@frappe.whitelist()
def log_payment_call(task_id, discussion_summary, customer_response, call_outcome=None, promised_amount=None, promised_payment_date=None, next_follow_up_date=None):
    """Log a customer follow-up call under a Payment Collection Task"""
    try:
        task = frappe.get_doc("Payment Collection Task", task_id)
        
        # Add to Call History
        task.append("call_history", {
            "call_date_and_time": frappe.utils.now_datetime(),
            "staff_member": frappe.session.user,
            "discussion_summary": discussion_summary,
            "customer_response": customer_response,
            "call_outcome": call_outcome,
            "promised_amount": promised_amount,
            "promised_payment_date": promised_payment_date,
            "next_follow_up_date": next_follow_up_date
        })
        
        # If promised details are entered, also create a Payment Commitment entry
        if promised_amount:
            task.append("payment_commitments", {
                "commitment_date": frappe.utils.today(),
                "promised_amount": promised_amount,
                "promised_payment_date": promised_payment_date,
                "status": "Pending",
                "remarks": f"Auto-created from call log: {discussion_summary[:100]}"
            })
            
        if task.status == "Open":
            task.status = "In Progress"
            
        if next_follow_up_date:
            task.next_follow_up_date = next_follow_up_date
        task.assigned_to = frappe.session.user
            
        task.save(ignore_permissions=True)
        
        # Auto-assign all other tasks for this customer to the current user
        other_tasks = frappe.get_all(
            "Payment Collection Task",
            filters={
                "customer": task.customer,
                "name": ["!=", task.name]
            },
            fields=["name"]
        )
        for ot in other_tasks:
            frappe.db.set_value("Payment Collection Task", ot.name, "assigned_to", frappe.session.user)
        frappe.db.commit()
        return task.as_dict()
    except Exception as e:
        frappe.log_error(f"Error logging call: {str(e)}")
        frappe.throw(f"Failed to log call: {str(e)}")

@frappe.whitelist()
def record_payment_receipt(task_id, amount_received, payment_mode, transaction_reference=None, remarks=None, next_follow_up_date=None, commitment_row_id=None, commitment_status=None):
    """Record a receipt of payment under a Payment Collection Task"""
    try:
        if payment_mode != "Cash" and not (transaction_reference and str(transaction_reference).strip()):
            msg = "Transaction Reference is mandatory for non-Cash payments."
            frappe.local.response['_error_message'] = msg
            frappe.throw(msg)
            
        task = frappe.get_doc("Payment Collection Task", task_id)
        
        # Validate next follow up date if there will be a remaining balance
        current_collected = sum(float(r.amount_received or 0) for r in task.payment_receipts)
        new_outstanding = float(task.payment_amount or 0) - (current_collected + float(amount_received))
        if new_outstanding > 0 and commitment_status == 'Partially Paid' and not next_follow_up_date:
            msg = "Next Follow-up Date is mandatory since there is a remaining outstanding balance."
            frappe.local.response['_error_message'] = msg
            frappe.throw(msg)
        
        # Add to Payment Receipts
        task.append("payment_receipts", {
            "receipt_date": frappe.utils.today(),
            "amount_received": amount_received,
            "payment_mode": payment_mode,
            "transaction_reference": transaction_reference,
            "received_by": frappe.session.user,
            "remarks": remarks
        })
        
        if next_follow_up_date:
            task.next_follow_up_date = next_follow_up_date
            
        if commitment_row_id and commitment_status:
            for c in task.payment_commitments:
                if c.name == commitment_row_id:
                    c.status = commitment_status
                    if remarks:
                        c.remarks = remarks
                    if amount_received:
                        c.amount_paid = amount_received
                    if next_follow_up_date:
                        c.next_follow_up_date = next_follow_up_date

                    break
                    
        task.save()
        
        # Auto-create new commitment if there is still an outstanding balance
        # if commitment_row_id and commitment_status in ["Received", "Partially Paid"]:
        #     collected_amt = sum(float(r.amount_received or 0) for r in task.payment_receipts)
        #     outstanding_amt = float(task.payment_amount or 0) - collected_amt
        #     if outstanding_amt > 0:
        #         task.append("payment_commitments", {
        #             "commitment_date": frappe.utils.today(),
        #             "promised_payment_date": next_follow_up_date,
        #             "promised_amount": outstanding_amt,
        #             "status": "Pending",
        #             "remarks": f"Auto-generated for remaining balance after payment on {frappe.utils.today()}"
        #         })
        #         task.save()
        frappe.db.commit()
        return task.as_dict()
    except Exception as e:
        frappe.log_error(f"Error recording receipt: {str(e)}")
        frappe.throw(f"Failed to record receipt: {str(e)}")

@frappe.whitelist()
def cancel_task(doctype, task_id):
    """Cancel a task and all its pending commitments"""
    try:
        task = frappe.get_doc(doctype, task_id)
        task.status = "Cancelled"
        
        if hasattr(task, "payment_commitments"):
            for c in task.payment_commitments:
                if c.status == "Pending":
                    c.status = "Cancelled"
                    c.remarks = "Auto-cancelled with task"
                    
        task.save()
        frappe.db.commit()
        return task.as_dict()
    except Exception as e:
        frappe.log_error(f"Error cancelling task: {str(e)}")
        frappe.throw(f"Failed to cancel task: {str(e)}")

@frappe.whitelist()
def update_commitment_status(task_id, commitment_row_id, status, remarks=None, amount_paid=None, next_follow_up_date=None):
    """Update status of a Payment Commitment"""
    try:
        task = frappe.get_doc("Payment Collection Task", task_id)
        
        found = False
        for c in task.payment_commitments:
            if c.name == commitment_row_id:
                c.status = status
                if remarks:
                    c.remarks = remarks
                found = True
                break
                
        if not found:
            frappe.throw(f"Commitment row {commitment_row_id} not found in task {task_id}")
            
        if next_follow_up_date:
            task.next_follow_up_date = next_follow_up_date
            
        task.save()
        frappe.db.commit()
        return task.as_dict()
    except Exception as e:
        frappe.log_error(f"Error updating commitment: {str(e)}")
        frappe.throw(f"Failed to update commitment: {str(e)}")
@frappe.whitelist()
def edit_commitment(task_id, commitment_row_id, promised_amount=None, expected_date=None, next_follow_up_date=None):
    """Edit fields of a Payment Commitment and optionally the Task's next follow up date"""
    try:
        task = frappe.get_doc("Payment Collection Task", task_id)
        
        found = False
        for c in task.payment_commitments:
            if c.name == commitment_row_id:
                if promised_amount:
                    c.promised_amount = promised_amount
                if expected_date:
                    c.promised_payment_date = expected_date
                found = True
                break
                
        if not found:
            frappe.throw(f"Commitment row {commitment_row_id} not found in task {task_id}")
            
        if next_follow_up_date:
            task.next_follow_up_date = next_follow_up_date
            
        task.save(ignore_permissions=True)
        frappe.db.commit()
        return task.as_dict()
    except Exception as e:
        frappe.log_error(f"Error editing commitment: {str(e)}")
        frappe.throw(f"Failed to edit commitment: {str(e)}")
            
        task.save()
        frappe.db.commit()
        return task.as_dict()
    except Exception as e:
        frappe.log_error(f"Error updating commitment: {str(e)}")
        frappe.throw(f"Failed to update commitment: {str(e)}")

@frappe.whitelist()
def update_task_details(task_id, updates):
    """Update main task details like purpose, amount, etc."""
    try:
        if isinstance(updates, str):
            import json
            updates = json.loads(updates)
            
        task = frappe.get_doc("Payment Collection Task", task_id)
        
        for field, value in updates.items():
            if hasattr(task, field):
                setattr(task, field, value)
                
        task.save()
        frappe.db.commit()
        return task.as_dict()
    except Exception as e:
        frappe.log_error(f"Error updating task: {str(e)}")
        frappe.throw(f"Failed to update task: {str(e)}")

@frappe.whitelist()
def update_receipt_details(task_id, receipt_row_id, updates):
    """Update details of a specific payment receipt row"""
    try:
        if isinstance(updates, str):
            import json
            updates = json.loads(updates)
            
        task = frappe.get_doc("Payment Collection Task", task_id)
        
        found = False
        for receipt in task.payment_receipts:
            if receipt.name == receipt_row_id:
                for field, value in updates.items():
                    if hasattr(receipt, field):
                        setattr(receipt, field, value)
                        
                if receipt.payment_mode != "Cash" and not (receipt.transaction_reference and str(receipt.transaction_reference).strip()):
                    msg = "Transaction Reference is mandatory for non-Cash payments."
                    frappe.local.response['_error_message'] = msg
                    frappe.throw(msg)
                    
                found = True
                break
                
        if not found:
            frappe.throw(f"Receipt row {receipt_row_id} not found in task {task_id}")
            
        task.save()
        frappe.db.commit()
        return task.as_dict()
    except Exception as e:
        frappe.log_error(f"Error updating receipt: {str(e)}")
        frappe.throw(f"Failed to update receipt: {str(e)}")

@frappe.whitelist()
def run_verification_test():
    """Programmatic test runner to verify Payment Collection Task flow"""
    import frappe.utils
    print("🚀 Starting Payment Collection Task verification tests...")

    existing_cust = frappe.db.get_value("HD Customer", {"customer_name": "Verification Customer Ltd"}, "name")
    if not existing_cust:
        cust = frappe.get_doc({
            "doctype": "HD Customer",
            "customer_name": "Verification Customer Ltd"
        })
        cust.insert(ignore_permissions=True)
        customer_name_db = cust.name
        print(f"✅ Created customer: {customer_name_db}")
    else:
        customer_name_db = existing_cust
        print(f"ℹ️ Customer {customer_name_db} already exists")

    # Clean up any existing tasks for this customer
    tasks = frappe.get_all("Payment Collection Task", filters={"customer": customer_name_db}, pluck="name")
    for t in tasks:
        frappe.delete_doc("Payment Collection Task", t)
    print(f"🧹 Cleaned up {len(tasks)} existing tasks.")

    # 2. Create a Payment Collection Task
    print("📝 Step 1: Creating a Payment Collection Task...")
    task = frappe.get_doc({
        "doctype": "Payment Collection Task",
        "customer": customer_name_db,
        "purpose_type": "Software Payment",
        "task_description": "Testing the calculation of outstanding amount.",
        "assigned_to": "Administrator",
        "contact_person": "Jane Doe",
        "mobile_number": "9876543210",
        "payment_amount": 10000.0,
        "priority": "High",
        "status": "Open"
    })
    task.insert(ignore_permissions=True)
    task_name = task.name
    print(f"✅ Created Task {task_name}. Checking initial math...")

    # Verify initial values
    assert task.collected_amount == 0.0, f"Expected 0 collected, got {task.collected_amount}"
    assert task.outstanding_amount == 10000.0, f"Expected 10000 outstanding, got {task.outstanding_amount}"
    assert task.status == "Open", f"Expected status Open, got {task.status}"
    print("👍 Initial math checks passed!")

    # 3. Log a Follow-up Call with Commitment
    print("📞 Step 2: Logging call with a payment promise/commitment...")
    updated_task_dict = log_payment_call(
        task_id=task_name,
        discussion_summary="Customer promised to pay half by tomorrow.",
        customer_response="Promised Payment",
        call_outcome="Commitment Recorded",
        promised_amount=6000.0,
        promised_payment_date=frappe.utils.add_days(frappe.utils.today(), 1),
        next_follow_up_date=frappe.utils.add_days(frappe.utils.today(), 1)
    )

    # Fetch task again to verify
    task = frappe.get_doc("Payment Collection Task", task_name)
    assert len(task.call_history) == 1, "Expected 1 call log"
    assert len(task.payment_commitments) == 1, "Expected 1 commitment"
    assert task.payment_commitments[0].promised_amount == 6000.0, "Expected 6000 promise"
    assert task.payment_commitments[0].status == "Pending", "Expected Pending status"
    assert str(task.next_follow_up_date) == str(frappe.utils.add_days(frappe.utils.today(), 1)), "Expected correct follow-up date"
    print("👍 Call log and commitment verified!")

    # 4. Record Partial Payment Receipt
    print("💳 Step 3: Recording a partial payment receipt...")
    record_payment_receipt(
        task_id=task_name,
        amount_received=4000.0,
        payment_mode="Bank Transfer",
        transaction_reference="TXN987654",
        remarks="Received partial payment via IMPS"
    )

    task = frappe.get_doc("Payment Collection Task", task_name)
    assert task.collected_amount == 4000.0, f"Expected 4000 collected, got {task.collected_amount}"
    assert task.outstanding_amount == 6000.0, f"Expected 6000 outstanding, got {task.outstanding_amount}"
    assert task.status == "Partially Paid", f"Expected auto status Partially Paid, got {task.status}"
    print("👍 Partial payment math and status auto-transition verified!")

    # 5. Verify Completed Status validation constraint
    print("🚫 Step 4: Testing Completed status validation block...")
    task.status = "Completed"
    try:
        task.save()
        raise AssertionError("Should have blocked marking task as Completed with outstanding balance!")
    except frappe.ValidationError as e:
        print(f"✅ Successfully blocked: '{str(e)}'")

    # 6. Record remaining payment
    print("💳 Step 5: Recording remaining payment...")
    record_payment_receipt(
        task_id=task_name,
        amount_received=6000.0,
        payment_mode="Online"
    )

    task = frappe.get_doc("Payment Collection Task", task_name)
    assert task.collected_amount == 10000.0, f"Expected 10000 collected, got {task.collected_amount}"
    assert task.outstanding_amount == 0.0, f"Expected 0 outstanding, got {task.outstanding_amount}"
    print("👍 Full payment calculation verified!")

    # 7. Close Task
    print("🔒 Step 6: Marking fully paid task as Completed...")
    task.status = "Completed"
    task.save()
    print(f"✅ Task {task_name} successfully set to Completed!")

    print("\n🎉 ALL PAYMENT MODULE VERIFICATION TESTS PASSED SUCCESSFULLY! 🎉")
    return "Verification success"
@frappe.whitelist()
def get_current_user():
    return frappe.session.user

@frappe.whitelist()
def get_call_management_logs(task_id):
    """Get standalone call management logs for a task"""
    try:
        logs = frappe.get_all(
            "Call Management Log",
            filters={"payment_collection_task": task_id},
            fields=[
                "name", "call_date_and_time", "staff_member", 
                "customer_response", "call_outcome", "discussion_summary",
                "promised_amount", "promised_payment_date", "next_follow_up_date"
            ],
            order_by="call_date_and_time desc"
        )
        return logs
    except Exception as e:
        frappe.log_error(f"Error fetching call management logs: {str(e)}")
        return []

@frappe.whitelist()
def log_management_call(task_id, discussion_summary, customer_response, call_outcome=None, promised_amount=None, promised_payment_date=None, next_follow_up_date=None):
    """Log a standalone call in Call Management Log"""
    try:
        doc = frappe.get_doc({
            "doctype": "Call Management Log",
            "payment_collection_task": task_id,
            "call_date_and_time": frappe.utils.now_datetime(),
            "staff_member": frappe.session.user,
            "discussion_summary": discussion_summary,
            "customer_response": customer_response,
            "call_outcome": call_outcome,
            "promised_amount": promised_amount,
            "promised_payment_date": promised_payment_date,
            "next_follow_up_date": next_follow_up_date
        })
        doc.insert(ignore_permissions=True)
        
        # Also mirror to Payment Collection Task child tables
        task_doc = frappe.get_doc("Payment Collection Task", task_id)
        task_doc.append("call_history", {
            "call_date_and_time": doc.call_date_and_time,
            "staff_member": doc.staff_member,
            "customer_response": doc.customer_response,
            "call_outcome": doc.call_outcome,
            "discussion_summary": doc.discussion_summary,
            "next_follow_up_date": doc.next_follow_up_date
        })
        
        if promised_amount or promised_payment_date:
            task_doc.append("payment_commitments", {
                "commitment_date": frappe.utils.nowdate(),
                "promised_amount": promised_amount,
                "promised_payment_date": promised_payment_date,
                "status": "Pending",
                "remarks": f"From Call Log: {discussion_summary}"
            })
            
        if next_follow_up_date:
            task_doc.next_follow_up_date = next_follow_up_date
            
        if task_doc.status == "Open":
            task_doc.status = "In Progress"
            
        task_doc.assigned_to = frappe.session.user
            
        task_doc.save(ignore_permissions=True)

        # Auto-assign ALL other tasks for this customer to the current user
        other_tasks = frappe.get_all(
            "Payment Collection Task",
            filters={
                "customer": task_doc.customer,
                "name": ["!=", task_doc.name]
            },
            fields=["name"]
        )
        for ot in other_tasks:
            frappe.db.set_value("Payment Collection Task", ot.name, "assigned_to", frappe.session.user)

        frappe.db.commit()
        return doc.as_dict()
    except Exception as e:
        frappe.log_error(f"Error logging management call: {str(e)}")
        frappe.throw(f"Failed to log management call: {str(e)}")

@frappe.whitelist()
def update_task_follow_up_date(task_id, call_log_id, next_follow_up_date):
    try:
        task_doc = frappe.get_doc("Payment Collection Task", task_id)
        if next_follow_up_date:
            task_doc.next_follow_up_date = next_follow_up_date
            task_doc.save(ignore_permissions=True)
            
            if call_log_id:
                frappe.db.set_value("Payment Collection Call History", call_log_id, "next_follow_up_date", next_follow_up_date)
            
            frappe.db.commit()
            
        return task_doc.as_dict()
    except Exception as e:
        frappe.log_error(f"Error updating follow up date: {str(e)}")
        frappe.throw(f"Failed to update follow up date: {str(e)}")

@frappe.whitelist()
def get_customer_pending_tasks(customer, current_task_id=None):
    """Fetch other pending tasks for the same customer (both Payment Collection and Call Management)"""
    try:
        if not customer:
            return []

        # Find all Payment Collection Tasks for this customer
        # that are not the current task
        payment_tasks = frappe.get_all(
            "Payment Collection Task",
            filters={
                "customer": customer,
                "name": ["!=", current_task_id] if current_task_id else ["is", "set"]
            },
            fields=["name", "purpose_type", "status", "priority", "task_description", "next_follow_up_date", "payment_amount", "collected_amount", "outstanding_amount"],
            order_by="next_follow_up_date asc, modified desc"
        )
        
        # In this module, Call Management Tasks are essentially the same Doctypes, 
        # but the task_type might differ or they are separated by module logic.
        # However, the user mentioned "Call Management Tasks" which might be 
        # tracked as a different Doctype "Call Management Task" OR just "Payment Collection Task"
        # Let's check if there's a Doctype named "Call Management Task".
        # Actually, looking at the code previously, both modules often use "Payment Collection Task" 
        # but filter by task_type or the list pages differ. 
        # Let's just return what we fetched since it's the same Doctype!
        
        # Add a flag to distinguish type if needed, but since it's all in Payment Collection Task Doctype,
        # we just return the list.
        return payment_tasks

    except Exception as e:
        frappe.log_error(f"Error fetching customer pending tasks: {str(e)}")
        return []
@frappe.whitelist()
def get_customer_history(customer):
    """Fetch combined call logs, commitments, and receipts for all tasks of a customer"""
    try:
        if not customer:
            return {"calls": [], "commitments": [], "receipts": []}

        tasks = frappe.get_all("Payment Collection Task", filters={"customer": customer}, fields=["name"])
        task_names = [t.name for t in tasks]

        if not task_names:
            return {"calls": [], "commitments": [], "receipts": []}

        calls = frappe.get_all("Payment Collection Call History", filters={"parent": ["in", task_names]}, fields=["*", "parent"], order_by="call_date_and_time desc")
        commitments = frappe.get_all("Payment Collection Commitment", filters={"parent": ["in", task_names]}, fields=["*", "parent"], order_by="commitment_date desc")
        receipts = frappe.get_all("Payment Collection Receipt", filters={"parent": ["in", task_names]}, fields=["*", "parent"], order_by="receipt_date desc")

        return {
            "calls": calls,
            "commitments": commitments,
            "receipts": receipts
        }
    except Exception as e:
        frappe.log_error(f"Error fetching customer history: {str(e)}")
        return {"calls": [], "commitments": [], "receipts": []}

@frappe.whitelist()
def update_customer_contact_details(customer, contact_person=None, mobile_number=None, alternate_mobile=None):
    try:
        tasks = frappe.get_all(
            "Payment Collection Task",
            filters={
                "customer": customer,
                "status": ["in", ["Open", "In Progress"]]
            },
            fields=["name"]
        )
        for t in tasks:
            doc = frappe.get_doc("Payment Collection Task", t.name)
            changed = False
            changes = []
            
            if contact_person is not None and doc.contact_person != contact_person:
                changes.append(f"Contact Person from '{doc.contact_person}' to '{contact_person}'")
                doc.contact_person = contact_person
                changed = True
                
            if mobile_number is not None and doc.mobile_number != mobile_number:
                changes.append(f"Mobile Number from '{doc.mobile_number}' to '{mobile_number}'")
                doc.mobile_number = mobile_number
                changed = True
                
            if alternate_mobile is not None and doc.alternate_mobile != alternate_mobile:
                changes.append(f"Alternate Mobile from '{doc.alternate_mobile}' to '{alternate_mobile}'")
                doc.alternate_mobile = alternate_mobile
                changed = True
                
            if changed:
                doc.flags.ignore_permissions = True
                doc.save()
                doc.add_comment("Comment", "Updated Customer Contact Details: " + ", ".join(changes))
        
        frappe.db.commit()
        return {"status": "success"}
    except Exception as e:
        frappe.log_error(f"Error updating customer contact details: {str(e)}")
        frappe.throw(f"Failed to update customer contact details: {str(e)}")

@frappe.whitelist()
def get_all_commitments_and_receipts():
    """Fetch all payment commitments and receipts across all customers for Accounts team view"""
    
    commitments = frappe.db.sql("""
        SELECT 
            c.name, c.parent as task, c.commitment_date, c.promised_amount, 
            c.promised_payment_date, c.status, c.remarks,
            cust.customer_name as customer, t.outstanding_amount, t.payment_amount, t.collected_amount, t.next_follow_up_date as task_next_follow_up_date
        FROM `tabPayment Collection Commitment` c
        JOIN `tabPayment Collection Task` t ON c.parent = t.name
        LEFT JOIN `tabHD Customer` cust ON t.customer = cust.name
        ORDER BY c.promised_payment_date ASC, c.creation DESC
    """, as_dict=True)
    
    receipts = frappe.db.sql("""
        SELECT 
            r.name, r.parent as task, r.receipt_date, r.amount_received, 
            r.payment_mode, r.transaction_reference, r.remarks,
            cust.customer_name as customer
        FROM `tabPayment Collection Receipt` r
        JOIN `tabPayment Collection Task` t ON r.parent = t.name
        LEFT JOIN `tabHD Customer` cust ON t.customer = cust.name
        ORDER BY r.receipt_date DESC, r.modified DESC, r.idx DESC
    """, as_dict=True)
    
    return {
        "commitments": commitments,
        "receipts": receipts
    }
