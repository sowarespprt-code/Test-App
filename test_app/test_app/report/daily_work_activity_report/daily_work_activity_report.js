// Copyright (c) 2026, soware and contributors
// For license information, please see license.txt

frappe.query_reports["Daily Work Activity Report"] = {
  filters: [
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      default: frappe.datetime.get_today(),
      reqd: 1,
      on_change: function () {},
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      default: frappe.datetime.get_today(),
      on_change: function () {},
      reqd: 1,
    },
    {
      fieldname: "activity_type",
      label: __("Activity Type"),
      fieldtype: "Select",
      options:
        "\nTask Created\nCall Logged\nPayment Received\nPromise Recorded\nOther Activity",
      default: "",
      on_change: function () {},
    },
    {
      fieldname: "task",
      label: __("Task"),
      fieldtype: "Link",
      options: "Payment Collection Task",
      default: "",
      on_change: function () {},
    },
  ],

  onload: async function (report) {
    // Save the original refresh method once for this report instance.
    if (!report._daily_work_original_refresh) {
      report._daily_work_original_refresh =
        report.refresh.bind(report);
    }

    // Block automatic refresh requests for this report instance.
    report.refresh = function () {
      return Promise.resolve();
    };

    await report.set_filter_value({
      from_date: frappe.datetime.get_today(),
      to_date: frappe.datetime.get_today(),
      staff: "",
      view: "",
      activity_type: "",
      task: "",
    });

    report.page.add_inner_button(__("Show Report"), function () {
      // Explicitly run the original refresh using current filters.
      return report._daily_work_original_refresh();
    });

    report.page.add_inner_button(__("Payment Module"), function () {
      window.location.href = "/helpdesk/payment-collection";
    });
  },
};