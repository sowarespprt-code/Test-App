function debounce(fn, delay) {
    let timer = null;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

frappe.query_reports["Custom Ticket Report"] = {
    filters: [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.datetime.month_start()
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.datetime.month_end()
        },
        {
            fieldname: "custom_customer_name",
            label: "Customer Name",
            fieldtype: "Link",
            options: "HD Customer"
        },
        {
            fieldname: "priority",
            label: "Priority",
            fieldtype: "Select",
            options: "\nLow\nMedium\nHigh\nUrgent"
        }
    ],
    
    onload: function(report) {
        // Add Search Customer button AFTER priority field (at the end, same line)
        setTimeout(function() {
            // Make sure filters are displayed inline first
            $('.page-form .form-section').css({
                'display': 'flex',
                'flex-wrap': 'wrap',
                'gap': '10px',
                'align-items': 'flex-end'
            });
            
            const priority_wrapper = report.page.fields_dict.priority.$wrapper;
            
            if (priority_wrapper) {
                // Remove existing button if any
                $('#customer-search-btn-wrapper').remove();
                
                // Create button wrapper with inline-block display
                const search_button_wrapper = $(`
                    <div id="customer-search-btn-wrapper" class="frappe-control" 
                         style="display: inline-block; vertical-align: top; min-width: 150px;">
                        <div class="form-group" style="margin-bottom: 0;">
                            <div class="clearfix">
                                <label class="control-label" style="padding-right: 0px; visibility: hidden;">Search</label>
                            </div>
                            <div class="control-input-wrapper">
                                <div class="control-input">
                                    <button class="btn btn-default btn-sm" 
                                            id="customer-search-btn"
                                            style="width: 100%; 
                                                   background: #000; 
                                                   color: #fff; 
                                                   border: 1px solid #000;
                                                   border-radius: var(--border-radius);
                                                   font-weight: 500;
                                                   font-size: 12px;
                                                   display: flex;
                                                   align-items: center;
                                                   justify-content: center;
                                                   gap: 6px;
                                                   transition: all 0.2s;
                                                   cursor: pointer;
                                                   padding: 5px 12px;
                                                   white-space: nowrap;">
                                        <svg style="width: 14px; height: 14px; flex-shrink: 0;" 
                                             xmlns="http://www.w3.org/2000/svg" 
                                             viewBox="0 0 24 24" 
                                             fill="none" 
                                             stroke="currentColor" 
                                             stroke-width="2.5"
                                             stroke-linecap="round"
                                             stroke-linejoin="round">
                                            <circle cx="11" cy="11" r="8"></circle>
                                            <path d="m21 21-4.35-4.35"></path>
                                        </svg>
                                        <span>Search Customer</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `);
                
                // Insert AFTER priority field
                priority_wrapper.after(search_button_wrapper);
                
                // Add hover effect
                $('#customer-search-btn').hover(
                    function() {
                        $(this).css({
                            'background': '#333',
                            'box-shadow': '0 1px 3px rgba(0,0,0,0.12)'
                        });
                    },
                    function() {
                        $(this).css({
                            'background': '#000',
                            'box-shadow': 'none'
                        });
                    }
                );
                
                // Add click handler
                $('#customer-search-btn').on('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    show_customer_search_popup(report);
                });
            }
        }, 600);

        // NO auto-refresh bindings here: typing in filters will not refresh or clear values

        // Make report mobile responsive
        add_mobile_styles();
        
        // Export actions
        report.page.add_action_item(__("Export Excel"), function() {
            export_report(report, "xlsx");
        });
        
        report.page.add_action_item(__("Export CSV"), function() {
            export_report(report, "csv");
        });
    }
};

// Add mobile responsive styles
function add_mobile_styles() {
    if (!$('#custom-report-mobile-styles').length) {
        $('head').append(`
            <style id="custom-report-mobile-styles">
                /* Mobile responsive styles for Custom Ticket Report */
                @media (max-width: 768px) {
                    .report-wrapper .datatable {
                        font-size: 11px !important;
                    }
                    
                    .report-wrapper .datatable .dt-cell__content {
                        white-space: normal !important;
                        word-wrap: break-word !important;
                    }
                    
                    .report-wrapper .datatable .dt-scrollable {
                        overflow-x: auto !important;
                    }
                    
                    /* Make all columns visible on mobile */
                    .report-wrapper .datatable .dt-cell,
                    .report-wrapper .datatable .dt-header {
                        min-width: 80px !important;
                    }
                    
                    /* Adjust specific columns for mobile */
                    .report-wrapper .datatable .dt-cell[data-col-index="0"],
                    .report-wrapper .datatable .dt-header[data-col-index="0"] {
                        min-width: 50px !important;
                    }
                    
                    .report-wrapper .datatable .dt-cell[data-col-index="3"],
                    .report-wrapper .datatable .dt-header[data-col-index="3"] {
                        min-width: 150px !important;
                    }
                    
                    /* Filter fields responsive */
                    .page-form .frappe-control {
                        width: 100% !important;
                    }
                    
                    /* Stack filters vertically on mobile */
                    .page-form .form-section {
                        display: flex;
                        flex-direction: column;
                    }
                }
                
                /* Ensure horizontal scroll on mobile for table */
                @media (max-width: 768px) {
                    .report-wrapper {
                        overflow-x: auto !important;
                        -webkit-overflow-scrolling: touch !important;
                    }
                    
                    .dt-scrollable {
                        width: 100% !important;
                        overflow-x: auto !important;
                    }
                }
            </style>
        `);
    }
}

// Export function
function export_report(report, file_format) {
    frappe.call({
        method: "frappe.desk.query_report.run",
        type: "GET",
        args: {
            report_name: report.report_name,
            filters: report.get_values(),
            file_format_type: file_format
        },
        callback: function(r) {
            if (!r.exc && r.message) {
                const url = r.message;
                const link = document.createElement("a");
                link.href = url;
                link.download = report.report_name + "." + file_format;
                link.click();
            }
        }
    });
}

// Customer Search Popup
function show_customer_search_popup(report) {
    let search_results = [];
    let selected_customer = null;
    let debounce_timer = null;
    
    const dialog = new frappe.ui.Dialog({
        title: __('Search Customer'),
        fields: [
            {
                fieldname: 'search_input',
                label: __('Search'),
                fieldtype: 'Data',
                placeholder: 'Search by name, code, address, phone...'
            },
            {
                fieldname: 'results_html',
                fieldtype: 'HTML'
            }
        ],
        primary_action_label: __('Select'),
        primary_action: function() {
            if (selected_customer) {
                report.set_filter_value('custom_customer_name', selected_customer.name);
                dialog.hide();
            } else {
                frappe.msgprint(__('Please select a customer'));
            }
        }
    });
    
    // Search input handler
    dialog.fields_dict.search_input.$input.on('input', function() {
        const query = $(this).val().trim();
        
        if (debounce_timer) {
            clearTimeout(debounce_timer);
        }
        
        if (query.length >= 1) {
            show_loading();
            debounce_timer = setTimeout(function() {
                search_customers(query);
            }, 500);
        } else {
            show_initial_state();
        }
    });
    
    function show_loading() {
        dialog.fields_dict.results_html.$wrapper.html(`
            <div style="text-align: center; padding: 40px; color: #888;">
                <div class="spinner-border spinner-border-sm" role="status"></div>
                <p style="margin-top: 10px;">Searching...</p>
            </div>
        `);
    }
    
    function show_initial_state() {
        dialog.fields_dict.results_html.$wrapper.html(`
            <div style="text-align: center; padding: 40px; color: #888;">
                <svg style="width: 40px; height: 40px; margin: 0 auto; opacity: 0.5;" 
                     xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" 
                     fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.35-4.35"></path>
                </svg>
                <p style="margin-top: 15px;">Type to search customers</p>
            </div>
        `);
    }
    
    function search_customers(query) {
        frappe.call({
            method: 'helpdesk.api.customer_api.search_hd_customers',
            args: { 
                search_term: query 
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    search_results = r.message;
                    render_results();
                } else {
                    show_no_results();
                }
            },
            error: function(err) {
                console.error('Search error:', err);
                dialog.fields_dict.results_html.$wrapper.html(`
                    <div style="text-align: center; padding: 40px; color: #d9534f;">
                        <p>Error loading results</p>
                    </div>
                `);
            }
        });
    }
    
    function show_no_results() {
        dialog.fields_dict.results_html.$wrapper.html(`
            <div style="text-align: center; padding: 40px; color: #888;">
                <p>No customers found</p>
            </div>
        `);
    }
    
    function render_results() {
        let html = `
            <div style="max-height: 350px; overflow-y: auto; margin-top: 10px;">
                <div style="font-size: 11px; color: #888; margin-bottom: 10px;">
                    Found ${search_results.length} customer(s)
                </div>
        `;
        
        search_results.forEach(function(customer, idx) {
            const is_selected = selected_customer && selected_customer.name === customer.name;
            html += `
                <div class="customer-item" data-idx="${idx}" 
                     style="padding: 10px; margin-bottom: 8px; border: 1px solid ${is_selected ? '#2490ef' : '#d1d8dd'}; 
                            border-radius: 4px; cursor: pointer; background: ${is_selected ? '#e8f4fd' : '#fff'};">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <strong style="font-size: 13px;">${customer.customer_name || ''}</strong>
                        ${customer.custom_customercode ? `<span style="font-size: 11px; color: #888;">${customer.custom_customercode}</span>` : ''}
                    </div>
                    <div style="font-size: 11px; color: #666;">
                        ${customer.custom_productname ? `Product: ${customer.custom_productname}` : ''}
                        ${customer.custom_productname && customer.custom_place ? ' | ' : ''}
                        ${customer.custom_place ? `Place: ${customer.custom_place}` : ''}
                        ${(customer.custom_productname || customer.custom_place) && customer.custom_phone001 ? ' | ' : ''}
                        ${customer.custom_phone001 ? `Phone: ${customer.custom_phone001}` : ''}
                    </div>
                </div>
            `;
        });
        
        html += `</div>`;
        dialog.fields_dict.results_html.$wrapper.html(html);
        
        // Add click handlers
        $('.customer-item').on('click', function() {
            const idx = $(this).data('idx');
            selected_customer = search_results[idx];
            render_results();
        });
        
        // Hover effect
        $('.customer-item').hover(
            function() {
                const idx = $(this).data('idx');
                if (!selected_customer || selected_customer.name !== search_results[idx].name) {
                    $(this).css({'background': '#f8f9fa', 'border-color': '#adb5bd'});
                }
            },
            function() {
                const idx = $(this).data('idx');
                if (!selected_customer || selected_customer.name !== search_results[idx].name) {
                    $(this).css({'background': '#fff', 'border-color': '#d1d8dd'});
                }
            }
        );
    }
    
    show_initial_state();
    dialog.show();
    
    setTimeout(function() {
        dialog.fields_dict.search_input.$input.focus();
    }, 300);
}
