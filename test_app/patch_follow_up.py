import frappe

def run_patch():
    tasks = frappe.get_all("Payment Collection Task", fields=["name", "next_follow_up_date"])
    print(f"Total tasks found: {len(tasks)}")
    
    updated = 0
    for task_info in tasks:
        task = frappe.get_doc("Payment Collection Task", task_info.name)
        
        # Determine the latest date from call history
        latest_call_date = None
        if task.call_history:
            sorted_calls = sorted(
                task.call_history,
                key=lambda x: x.call_date_and_time or "",
                reverse=True
            )
            for call in sorted_calls:
                if call.next_follow_up_date:
                    latest_call_date = call.next_follow_up_date
                    break
                    
        # Determine the latest date from payment commitments
        latest_commitment_date = None
        if task.payment_commitments:
            sorted_commitments = sorted(
                task.payment_commitments,
                key=lambda x: x.commitment_date or "",
                reverse=True
            )
            for c in sorted_commitments:
                if c.next_follow_up_date:
                    latest_commitment_date = c.next_follow_up_date
                    break
        
        # Pick the most recent one (or just the latest call one)
        new_date = latest_call_date or latest_commitment_date
        print(f"Task {task.name}: curr={task.next_follow_up_date}, new={new_date}")
        
        if new_date and str(task.next_follow_up_date) != str(new_date):
            task.next_follow_up_date = new_date
            task.save(ignore_permissions=True)
            updated += 1
            
    frappe.db.commit()
    print(f"Updated {updated} tasks.")
    return f"Updated {updated} tasks."
