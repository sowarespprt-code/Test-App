function debounce(fn, delay) {
    let timer = null;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

frappe.query_reports["Custom Ticket Report"] = {
    add_index: 0,

    initial_depth: 1,

    get_datatable_options(options) {
        // Hide rows on first load
        if (!frappe.query_report.filters_set) {
            return Object.assign(options, {
                data: []   // Prevent automatic rendering
            });
        }
        return options;
    },
    
    filters: [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
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
        },
        {
            fieldname: "status",
            label: "Status",
            fieldtype: "Select",
            options: "\nNot Assigned\nIn Progress\nOther\nClosed"
        }
    ],
    
    onload: function(report) {
         report.set_filter_value("from_date", "");
        report.set_filter_value("to_date", "");
        report.set_filter_value("custom_customer_name", "");
        report.set_filter_value("priority", "");
        report.set_filter_value("status", "");
        
        // Clear the datatable on load
        if (report.datatable) {
            report.datatable.refresh([]);
        }
        // Add Search Customer button AFTER priority field (at the end, same line)
         // ✨ CHANGE 2: Clear the datatable on load to show empty state
        setTimeout(function() {
            if (report.datatable && report.datatable.datamanager) {
                report.datatable.refresh([]);
            }
        }, 100);
        
        setTimeout(function() {
            // ✨ FIRST: Disable auto-refresh for ALL filter fields
            setTimeout(function() {
                // ✨ Disable date field auto-refresh
                const from_date = report.get_filter("from_date");
                const to_date = report.get_filter("to_date");

                if (from_date) {
                    from_date.df.onchange = () => {};     // disable frappe handler
                    from_date.$input.off("change");       // disable DOM event
                    from_date.$input.off("blur");         // VERY important
                    from_date.$input.off("input");        // internal trigger
                }

                if (to_date) {
                    to_date.df.onchange = () => {};
                    to_date.$input.off("change");
                    to_date.$input.off("blur");
                    to_date.$input.off("input");
                }
                
                // Disable customer field auto-refresh
                report.page.fields_dict.custom_customer_name.$input.off('change awesomplete-selectcomplete');
                
                // Disable priority field auto-refresh
                report.page.fields_dict.priority.$input.off('change');
                
                // Disable status field auto-refresh
                report.page.fields_dict.status.$input.off('change');
                
                // ✨ CRITICAL: Completely disable onchange handlers
                report.page.fields_dict.from_date.df.onchange = null;
                report.page.fields_dict.to_date.df.onchange = null;
                report.page.fields_dict.priority.df.onchange = null;
                report.page.fields_dict.status.df.onchange = null;
            }, 2000);

            setTimeout(() => {
                // ✨ Disable from_date filter
                const from_date_filter = report.get_filter('from_date');
                if (from_date_filter) {
                    from_date_filter.df.onchange = null;
                    from_date_filter.$input.off('change');
                    from_date_filter.$input.off('blur');
                }
                
                // ✨ Disable to_date filter
                const to_date_filter = report.get_filter('to_date');
                if (to_date_filter) {
                    to_date_filter.df.onchange = null;
                    to_date_filter.$input.off('change');
                    to_date_filter.$input.off('blur');
                }
                
                // Disable customer filter
                const customer_filter = report.get_filter('custom_customer_name');
                if (customer_filter) {
                    customer_filter.df.onchange = () => {};  // disable refresh
                    customer_filter.$input.off('awesomplete-selectcomplete');
                    customer_filter.$input.off('focusout');
                    customer_filter.$input.off('change');
                }
                
                // ✨ Double-check: Disable priority and status onchange again
                const priority_filter = report.get_filter('priority');
                if (priority_filter) {
                    priority_filter.df.onchange = null;
                    priority_filter.$input.off('change');
                }
                
                const status_filter = report.get_filter('status');
                if (status_filter) {
                    status_filter.df.onchange = null;
                    status_filter.$input.off('change');
                }
            }, 2200);

            // Make sure filters are displayed inline first
            $('.page-form .form-section').css({
                'display': 'flex',
                'flex-wrap': 'wrap',
                'gap': '10px',
                'align-items': 'flex-end'
            });

            
            
            const custom_customer_name_wrapper = report.page.fields_dict.custom_customer_name.$wrapper;
            
            if (custom_customer_name_wrapper) {
               
                
                // Create button wrapper with inline-block display
                const search_button_wrapper = $(`
                    <div id="customer-search-btn-wrapper" class="frappe-control" 
                         style="display: inline-block; vertical-align: top; min-width: auto; margin-left: 4px !important;">
                        <div class="form-group" style="margin-bottom: 0;">
                            <div class="clearfix">
                                <label class="control-label" style="display:none;">Search</label>
                            </div>
                            <div class="control-input-wrapper">
                                <div class="control-input">
                                    <button class="btn btn-default btn-sm" 
                                            id="customer-search-btn"
                                            style="width: 100px; 
                                                   background: #000; 
                                                   color: #fff; 
                                                   border: 1px solid #000;
                                                   border-radius: var(--border-radius);
                                                   font-weight: 500;
                                                   font-size: 8px;
                                                   display: flex;
                                                   align-items: center;
                                                   justify-content: center;
                                                   gap: 2px;
                                                   transition: all 0.2s;
                                                   cursor: pointer;
                                                   padding: 5px 12px;
                                                   white-space: nowrap;">
                                        <svg style="width: 13px; height: 13px; flex-shrink: 0;" 
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
                custom_customer_name_wrapper.after(search_button_wrapper);
                
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

         // Add Show Report button next to Actions
        setTimeout(function() {
            // Check if button already exists
            if (!$('#show-report-btn').length) {
                const show_report_btn = $(`
                    <button class="btn btn-default btn-sm" 
                            id="show-report-btn"
                            style="background: #000; 
                                   color: #fff; 
                                   border: 1px solid #000;
                                   border-radius: var(--border-radius);
                                   font-weight: 500;
                                   margin-left: 8px;
                                   padding: 6px 14px;
                                   transition: all 0.2s;
                                   cursor: pointer;">
                        Show Report
                    </button>
                `);
                
                // Insert after the grey Actions button
                $('.page-head-content .standard-actions').append(show_report_btn);
                
                // Add hover effect
                $('#show-report-btn').hover(
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
                
                // Add click handler to refresh report
                $('#show-report-btn').on('click', function() {
                    report.refresh();
                });
            }
        }, 800);

        // ✨ CHANGE 4: Function to hide column filter inputs
        function hide_row_filters() {
            $('.dt-row-filter').hide();
            $('.dt-filter').hide();
            $('.data-table .form-control').hide();
            // ✨ NEW: More aggressive hiding of column filter inputs
            $('.dt-cell--header input[type="text"]').hide();
            $('.dt-cell--header .dt-dropdown').hide();
            $('.dt-scrollable .dt-cell--header input').hide();
        }

        // ✨ CHANGE 5: Initial hide - multiple attempts for reliability
        setTimeout(hide_row_filters, 100);
        setTimeout(hide_row_filters, 300);
        setTimeout(hide_row_filters, 500);
        setTimeout(hide_row_filters, 1000);

        // ✨ CHANGE 6: Hide again whenever report refreshes (fixed implementation)
        const originalRefresh = report.refresh.bind(report);
        report.refresh = function() {
            originalRefresh();
            setTimeout(hide_row_filters, 100);
            setTimeout(hide_row_filters, 300);
        };

        // ✨ CHANGE 7: Hide again when data table re-renders (very important)
        $(document).on('data-table-render', function () {
            hide_row_filters();
        });

        // ✨ CHANGE 8: Monitor for any DOM changes and hide filters
        const observer = new MutationObserver(function() {
            hide_row_filters();
        });
        
        setTimeout(function() {
            const reportWrapper = document.querySelector('.report-wrapper');
            if (reportWrapper) {
                observer.observe(reportWrapper, {
                    childList: true,
                    subtree: true
                });
            }
        }, 1000);
        
        // Make report mobile responsive
        add_mobile_styles();
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