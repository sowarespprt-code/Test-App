# Copyright (c) 2026, soware and contributors
# For license information, please see license.txt

# import frappe


import frappe
from frappe.utils import (
    add_days,
    get_datetime,
    getdate,
    strip_html,
)

from test_app.api.timeline import (
    get_comments,
    get_history,
)

def get_staff_name(user):
    if not user:
        return "Unknown"

    return (
        frappe.get_cached_value(
            "User",
            user,
            "full_name",
        )
        or user
    )


def execute(filters=None):
    filters = frappe._dict(filters or {})

    if not filters.from_date or not filters.to_date:
        frappe.throw(
            "From Date and To Date are required."
        )

    if getdate(filters.from_date) > getdate(
        filters.to_date
    ):
        frappe.throw(
            "From Date cannot be after To Date."
        )

    activities = get_activities(filters)

    if filters.view == "Activity Details":
        return get_detail_columns(), activities

    return (
        get_summary_columns(),
        summarize_activities(activities),
    )


def get_activities(filters):
    user = frappe.session.user

    can_view_all_staff = (
        user == "Administrator"
        or "System Manager" in frappe.get_roles(user)
    )

    selected_staff = filters.get("staff")

    if not can_view_all_staff:
        if selected_staff and selected_staff != user:
            frappe.throw(
                "You can only view your own work activities.",
                frappe.PermissionError,
            )

        selected_staff = user

    from_datetime = get_datetime(filters.from_date)
    until_datetime = get_datetime(
        add_days(filters.to_date, 1)
    )

    task_filters = {}

    if filters.get("task"):
        task_filters["name"] = filters.task

    # get_list applies the current user's task permissions.
    # Read in batches rather than silently limiting the report
    # to the first 20 or 500 tasks.
    task_names = []
    start = 0
    batch_size = 200

    while True:
        batch = frappe.get_list(
            "Payment Collection Task",
            filters=task_filters,
            fields=["name"],
            order_by="name asc",
            start=start,
            page_length=batch_size,
        )

        task_names.extend(row.name for row in batch)

        if len(batch) < batch_size:
            break

        start += batch_size

    activities = []
    seen = set()
    customer_cache = {}

    def add_activity(
        event_key,
        timestamp,
        staff,
        activity_type,
        task,
        customer,
        details,
        amount=0,
    ):
        if not timestamp:
            return

        timestamp = get_datetime(timestamp)

        if not (
            from_datetime <= timestamp < until_datetime
        ):
            return

        if selected_staff and staff != selected_staff:
            return

        if (
            filters.get("activity_type")
            and activity_type != filters.activity_type
        ):
            return

        if event_key in seen:
            return

        seen.add(event_key)

        activities.append({
            "activity_date": getdate(timestamp),
            "staff": staff or "",
            "activity_type": activity_type,
            "task": task,
            "customer": customer,
            "amount": amount or 0,
            "details": strip_html(str(details or "")),
            "_timestamp": timestamp,
        })

    for task_name in task_names:
        task = frappe.get_doc(
            "Payment Collection Task",
            task_name,
        )

        # Recheck the actual document before reading child rows.
        if not task.has_permission("read"):
            continue

        customer_id = task.customer

        if customer_id not in customer_cache:
            customer_cache[customer_id] = (
                frappe.db.get_value(
                    "HD Customer",
                    customer_id,
                    "customer_name",
                )
                if customer_id
                else ""
            ) or customer_id or ""

        customer = customer_cache[customer_id]

        # Calls: use task history only, not its mirrored
        # standalone Call Management Log as another source.
        for call in task.get("call_history") or []:
            details = (
                f"Summary: {call.discussion_summary or '-'}; "
                f"Response: {call.customer_response or '-'}; "
                f"Outcome: {call.call_outcome or '-'}; "
                f"Call time: {call.call_date_and_time or '-'}; "
                f"Next follow-up: {call.next_follow_up_date or '-'}"
            )

            add_activity(
                event_key=f"call:{call.name}",
                timestamp=call.creation,
                staff=call.staff_member or call.owner,
                activity_type="Call Logged",
                task=task.name,
                customer=customer,
                details=details,
            )

        # Payment receipts.
        for receipt in task.get("payment_receipts") or []:
            details = (
                f"Payment date: {receipt.receipt_date or '-'}; "
                f"Mode: {receipt.payment_mode or '-'}; "
                f"Reference: "
                f"{receipt.transaction_reference or '-'}; "
                f"Remarks: {receipt.remarks or '-'}"
            )

            add_activity(
                event_key=f"receipt:{receipt.name}",
                timestamp=receipt.creation,
                staff=receipt.received_by or receipt.owner,
                activity_type="Payment Received",
                task=task.name,
                customer=customer,
                details=details,
                amount=receipt.amount_received,
            )

        # Promises are recorded separately from collections.
        for commitment in (
            task.get("payment_commitments") or []
        ):
            details = (
                f"Commitment date: "
                f"{commitment.commitment_date or '-'}; "
                f"Expected payment: "
                f"{commitment.promised_payment_date or '-'}; "
                f"Current status: {commitment.status or '-'}; "
                f"Remarks: {commitment.remarks or '-'}"
            )

            add_activity(
                event_key=f"commitment:{commitment.name}",
                timestamp=commitment.creation,
                staff=commitment.owner,
                activity_type="Promise Recorded",
                task=task.name,
                customer=customer,
                details=details,
                amount=commitment.promised_amount,
            )

        # Timeline field changes and task creation.
        # Exclude the child-table creation events because
        # we already added them above.
        for event in get_history(
            "Payment Collection Task",
            task.name,
        ):
            event_name = str(event.get("name") or "")

            # Calls, promises, and receipts are already collected
            # directly from the child tables.
            if event_name.startswith(
                ("call_", "comm_", "rec_")
            ):
                continue

            activity_type = (
                "Task Created"
                if event_name == f"creation_{task.name}"
                else "Other Activity"
            )

            event_key = (
                f"history:{task.name}:"
                f"{event_name}:"
                f"{event.get('action')}"
            )

            add_activity(
                event_key=event_key,
                timestamp=event.get("creation"),
                staff=event.get("owner"),
                activity_type=activity_type,
                task=task.name,
                customer=customer,
                details=event.get("action"),
            )

        # Comments follow the permissions already implemented
        # by your timeline's get_comments() function.
        for comment in get_comments(
            "Payment Collection Task",
            task.name,
        ):
            add_activity(
                event_key=f"comment:{comment.name}",
                timestamp=comment.creation,
                staff=comment.commented_by,
                activity_type="Other Activity",
                task=task.name,
                customer=customer,
                details=(
                    f"Comment: {comment.content or ''}"
                ),
            )

    activities.sort(
        key=lambda row: row["_timestamp"],
        reverse=True,
    )

    staff_names = {}

    for activity in activities:
        staff = activity.get("staff") or ""

        if staff not in staff_names:
            staff_names[staff] = get_staff_name(staff)

        activity["staff_name"] = staff_names[staff]
        activity.pop("_timestamp", None)

    return activities


def get_detail_columns():
    return [
        {
            "fieldname": "activity_date",
            "label": "Date",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "fieldname": "staff",
            "label": "Staff",
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "fieldname": "activity_type",
            "label": "Activity Type",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "fieldname": "task",
            "label": "Task",
            "fieldtype": "Link",
            "options": "Payment Collection Task",
            "width": 140,
        },
        {
            "fieldname": "customer",
            "label": "Customer",
            "fieldtype": "Data",
            "width": 220,
        },
        {
            "fieldname": "amount",
            "label": "Amount",
            "fieldtype": "Currency",
            "width": 130,
        },
        {
            "fieldname": "details",
            "label": "Details",
            "fieldtype": "Data",
            "width": 350,
        },
    ]


def get_summary_columns():
    return [
        {
            "fieldname": "activity_date",
            "label": "Date",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "fieldname": "staff_name",
            "label": "Staff Name",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "fieldname": "new_entries",
            "label": "New Tasks Created",
            "fieldtype": "Int",
            "width": 150,
        },
        {
            "fieldname": "follow_ups_done",
            "label": "Follow-ups Done",
            "fieldtype": "Int",
            "width": 140,
        },
        {
            "fieldname": "receipts",
            "label": "Payment Entries",
            "fieldtype": "Int",
            "width": 140,
        },
        {
            "fieldname": "amount_collected",
            "label": "Amount Collected",
            "fieldtype": "Currency",
            "width": 160,
        },
        {
            "fieldname": "promises",
            "label": "Promises Recorded",
            "fieldtype": "Int",
            "width": 150,
        },
        {
            "fieldname": "other_activities",
            "label": "Other Activities",
            "fieldtype": "Int",
            "width": 140,
        },
    ]


def summarize_activities(activities):
    grouped = {}
    staff_names = {}

    for activity in activities:
        staff = activity.get("staff") or ""

        key = (
            activity["activity_date"],
            staff,
        )

        if staff not in staff_names:
            staff_names[staff] = get_staff_name(staff)

        if key not in grouped:
            grouped[key] = {
                "activity_date": activity["activity_date"],
                "staff": staff,
                "staff_name": staff_names[staff],
                "new_entries": 0,
                "follow_ups_done": 0,
                "receipts": 0,
                "amount_collected": 0,
                "promises": 0,
                "other_activities": 0,
            }

        row = grouped[key]
        activity_type = activity["activity_type"]

        if activity_type == "Task Created":
            row["new_entries"] += 1

        elif activity_type == "Call Logged":
            row["follow_ups_done"] += 1

        elif activity_type == "Payment Received":
            row["receipts"] += 1
            row["amount_collected"] += float(
                activity.get("amount") or 0
            )

        elif activity_type == "Promise Recorded":
            row["promises"] += 1

        else:
            row["other_activities"] += 1

    return sorted(
        grouped.values(),
        key=lambda row: (
            str(row["activity_date"]),
            row["staff_name"],
            row["staff"],
        ),
        reverse=True,
    )
