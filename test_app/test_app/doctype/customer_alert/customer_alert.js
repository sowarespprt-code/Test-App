// Copyright (c) 2025, soware and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Customer Alert", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Customer Alert', {
    customer_name: function(frm) {
        // Skip if we're already viewing an existing document
        if (!frm.doc.customer_name || frm.doc.__islocal === 0) {
            return;
        }
        
        // Check for existing customer alert
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Customer Alert',
                filters: {
                    'customer_name': frm.doc.customer_name
                },
                fields: ['name', 'customer_name', 'remarks'],
                limit: 1
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    let existing_doc = r.message[0];
                    
                    // Show alert message
                    frappe.show_alert({
                        message: __('Customer Alert already exists for {0}. Loading existing record...', [frm.doc.customer_name]),
                        indicator: 'blue'
                    }, 5);
                    
                    // Navigate to existing document
                    setTimeout(() => {
                        frappe.set_route('Form', 'Customer Alert', existing_doc.name);
                    }, 800);
                } else {
                    // New customer - clear remarks field
                    frm.set_value('remarks', '');
                }
            }
        });
    },
    
    onload: function(frm) {
        // When loading an existing document, remarks are already populated
        // Make customer_name field read-only to prevent accidental changes
        if (!frm.doc.__islocal && frm.doc.customer_name) {
            frm.set_df_property('customer_name', 'read_only', 1);
        }
    },
    
    refresh: function(frm) {
        if (!frm.doc.__islocal) {
            // Make customer_name field read-only for existing documents
            frm.set_df_property('customer_name', 'read_only', 1);
            
            // Optional: Add custom button to view the HD Customer
            frm.add_custom_button(__('View HD Customer'), function() {
                frappe.set_route('Form', 'HD Customer', frm.doc.customer_name);
            });
        }
    }
});


