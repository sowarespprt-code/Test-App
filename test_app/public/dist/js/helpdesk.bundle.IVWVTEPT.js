(() => {
  // ../test_app/test_app/public/js/helpdesk.bundle.js
  frappe.provide("helpdesk.customer");
  helpdesk.customer.show_customer_modal = function(customer_name) {
    frappe.call({
      method: "test_app.api.helpdesk_customer.get_customer_details",
      args: { customer: customer_name },
      callback: function(r) {
        if (r.message) {
          let customer = r.message;
          let dialog_fields = [{
            fieldtype: "HTML",
            options: `<div class="text-center p-4">
                        <div style="width: 70px; height: 70px; margin: 0 auto 10px; 
                             border-radius: 50%; background: #5e64ff; color: white; 
                             display: flex; align-items: center; justify-content: center; 
                             font-size: 28px;">
                            ${customer.name[0].toUpperCase()}
                        </div>
                        <h4>${customer.name}</h4>
                    </div>`
          }];
          customer.fields.forEach((f) => {
            dialog_fields.push({
              fieldname: f.fieldname,
              label: f.label,
              fieldtype: f.fieldtype,
              default: f.value,
              options: f.options
            });
          });
          new frappe.ui.Dialog({
            title: "Customer Details",
            fields: dialog_fields,
            size: "large",
            primary_action_label: "Save",
            primary_action: function(values) {
              frappe.call({
                method: "frappe.client.set_value",
                args: {
                  doctype: "HD Customer",
                  name: customer_name,
                  fieldname: values
                },
                callback: () => {
                  frappe.show_alert("Customer updated");
                  this.hide();
                }
              });
            }
          }).show();
        }
      }
    });
  };
})();
//# sourceMappingURL=helpdesk.bundle.IVWVTEPT.js.map
