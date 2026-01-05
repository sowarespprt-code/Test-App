// Copyright (c) 2026, soware and contributors
// For license information, please see license.txt

frappe.query_reports["Customer - AMC Details"] = {
    "filters": [
        {
            "fieldname": "customer_name",
            "label": __("Customer Name"),
            "fieldtype": "Link",
            "options": "HD Customer",
            "width": "250px",
            "description": "Select customer then click Refresh"
        },
        {
            "fieldname": "amc_status",
            "label": __("AMC Status"),
            "fieldtype": "Select",
            "options": "All\nAMC Expired\nUpcoming Expiry",
            "default": "All",
            "width": "180px",
            "on_change": function() {
                let amc_status = frappe.query_report.get_filter_value('amc_status');
                let month_filter = frappe.query_report.get_filter('expiry_month');
                let year_filter = frappe.query_report.get_filter('expiry_year');
                
                if (amc_status == 'Upcoming Expiry') {
                    month_filter.df.hidden = 0;
                    year_filter.df.hidden = 0;
                } else {
                    month_filter.df.hidden = 1;
                    year_filter.df.hidden = 1;
                    frappe.query_report.set_filter_value('expiry_month', '');
                    frappe.query_report.set_filter_value('expiry_year', '');
                }
                month_filter.refresh();
                year_filter.refresh();
            }
        },
        {
            "fieldname": "expiry_month",
            "label": __("Month"),
            "fieldtype": "Select",
            "options": "\nJanuary\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
            "width": "150px",
            "hidden": 1
        },
        {
            "fieldname": "expiry_year",
            "label": __("Year"),
            "fieldtype": "Int",
            "width": "120px",
            "hidden": 1
        }
    ],
    
    "onload": function(report) {
        // Add mobile responsive styles
        add_mobile_styles();
    
        // ⭐ CLEAR ALL FILTERS ON PAGE LOAD - with delay
        setTimeout(function() {
            report.set_filter_value("customer_name", "");
            report.set_filter_value("amc_status", "All");
            
            const month_filter = report.get_filter('expiry_month');
            const year_filter = report.get_filter('expiry_year');
            
            if (month_filter && month_filter.$input) {
                month_filter.$input.val('');
                month_filter.set_value('');
            }
            if (year_filter && year_filter.$input) {
                year_filter.$input.val('');
                year_filter.set_value('');
            }
            
            console.log('✅ All filters cleared on page load');
        }, 50);
        
		// ⭐ BULLETPROOF SHOW/HIDE MONTH & YEAR FILTERS
        function toggle_filters() {
            const status = report.get_filter_value('amc_status');
            const show = (status === 'Upcoming Expiry');
            
            console.log('=== TOGGLE FILTERS ===');
            console.log('AMC Status:', status);
            console.log('Should Show:', show);
            
            // Month filter
            const month = report.get_filter('expiry_month');
            if(month && month.$wrapper) {
                console.log('Month wrapper before:', month.$wrapper[0]);
                console.log('Month wrapper classes before:', month.$wrapper.attr('class'));
                
                if(show) {
                    // AGGRESSIVE FORCE SHOW
                    month.df.hidden = 0;
                    month.$wrapper.removeClass('hide hide-control');
                    month.$wrapper.addClass('show-filter');
                    
                    // INLINE STYLES - Override everything
                    month.$wrapper.attr('style', 'display: block !important; visibility: visible !important; opacity: 1 !important; height: auto !important; width: 100% !important; position: relative !important; left: 0 !important; margin-top: 10px !important;');
                    
                    // jQuery show
                    month.$wrapper.show();
                    
                    console.log('✅ Month FORCE SHOWN');
                    console.log('Month wrapper classes after:', month.$wrapper.attr('class'));
                    console.log('Month wrapper style after:', month.$wrapper.attr('style'));
                    console.log('Month wrapper display:', month.$wrapper.css('display'));
                } else {
                    month.df.hidden = 1;
                    month.$wrapper.removeClass('show-filter');
                    month.$wrapper.addClass('hide hide-control');
                    month.$wrapper.attr('style', 'display: none !important; position: absolute !important; left: -9999px !important;');
                    month.$wrapper.hide();
                    
                    console.log('❌ Month HIDDEN');
                }
            } else {
                console.log('⚠️ Month filter NOT FOUND');
            }
            
            // Year filter
            const year = report.get_filter('expiry_year');
            if(year && year.$wrapper) {
                console.log('Year wrapper before:', year.$wrapper[0]);
                console.log('Year wrapper classes before:', year.$wrapper.attr('class'));
                
                if(show) {
                    // AGGRESSIVE FORCE SHOW
                    year.df.hidden = 0;
                    year.$wrapper.removeClass('hide hide-control');
                    year.$wrapper.addClass('show-filter');
                    
                    // INLINE STYLES - Override everything
                    year.$wrapper.attr('style', 'display: inline-block !important; visibility: visible !important; opacity: 1 !important; height: auto !important; width: auto !important; position: relative !important; left: 0 !important; margin-top: 10px !important; margin-left: 10px !important;');
                    
                    // jQuery show
                    year.$wrapper.show();
                    
                    console.log('✅ Year FORCE SHOWN');
                    console.log('Year wrapper classes after:', year.$wrapper.attr('class'));
                    console.log('Year wrapper style after:', year.$wrapper.attr('style'));
                    console.log('Year wrapper display:', year.$wrapper.css('display'));
                } else {
                    year.df.hidden = 1;
                    year.$wrapper.removeClass('show-filter');
                    year.$wrapper.addClass('hide hide-control');
                    year.$wrapper.attr('style', 'display: none !important; position: absolute !important; left: -9999px !important;');
                    year.$wrapper.hide();
                    
                    console.log('❌ Year HIDDEN');
                }
            } else {
                console.log('⚠️ Year filter NOT FOUND');
            }
            
            console.log('===================');
        }



        // ⭐ BIND TO STATUS CHANGE - MULTIPLE ATTEMPTS
        // ⭐ FIXED CHANGE EVENT BINDING + POLLING
        setTimeout(function() {
            console.log('🔍 Looking for status filter...');
            
            function bind_status_change() {
                const status_filter = report.get_filter('amc_status');
                if(status_filter) {
                    console.log('✅ Status filter FOUND');
                    
                    // Remove existing handlers
                    status_filter.$input.off('change');
                    
                    // Bind change event
                    status_filter.$input.on('change', function(e) {
                        console.log('🔥 STATUS CHANGED!', e.target.value);
                        setTimeout(toggle_filters, 10);
                    });
                    
                    // Also bind to Frappe's internal events
                    status_filter.df.onchange = function() {
                        console.log('🔥 STATUS ONCHANGE!');
                        setTimeout(toggle_filters, 10);
                    };
                    
                    // Test current status
                    toggle_filters();
                    return true;
                }
                return false;
            }
            
            // Retry binding multiple times
            let attempts = 0;
            const max_attempts = 10;
            const interval = setInterval(function() {
                attempts++;
                console.log(`Attempt ${attempts}/${max_attempts} to bind status filter`);
                
                if(bind_status_change() || attempts >= max_attempts) {
                    clearInterval(interval);
                }
            }, 500);
            
        }, 500);

        
        // Multiple retry attempts
        setTimeout(toggle_filters, 1500);
        setTimeout(toggle_filters, 2000);
        setTimeout(toggle_filters, 3000);

        // ⭐ POLLING - Check status every 500ms
        // ⭐ OPTIMIZED POLLING - Replace your existing polling code
        let previous_status = 'All';

        setInterval(function() {
            const status = report.get_filter_value('amc_status');
            if (status && status !== previous_status) {
                console.log('📊 Status changed via polling:', status);
                previous_status = status;
                
                // Multiple rapid toggles for reliability
                toggle_filters();
                setTimeout(toggle_filters, 50);
                setTimeout(toggle_filters, 150);
                setTimeout(toggle_filters, 300);
            }
        }, 250);  // 250ms - responsive but efficient

        // ⭐ HIDE LABELS WHEN FIELDS HAVE VALUES (Placeholder effect)
        // ⭐ FORCE Month/Year Labels OUTSIDE FIELDS - Custom layout
        setTimeout(function() {
            // Month field
            const month_filter = report.get_filter('expiry_month');
            if (month_filter && month_filter.$wrapper) {
                const month_label = month_filter.$wrapper.find('.control-label');
                const month_input = month_filter.$wrapper.find('.form-control');
                
                if (month_label.length && month_input.length) {
                    month_filter.$wrapper.css({
                        'display': 'flex',
                        'align-items': 'center',
                        'gap': '8px'
                    });
                    
                    month_label.css({
                        'width': 'auto',
                        'min-width': '50px',
                        'margin': '0',
                        'padding': '0',
                        'font-weight': '500',
                        'flex-shrink': '0'
                    });
                    
                    month_input.parent().css({
                        'flex': '1',
                        'display': 'inline-block'
                    });
                    month_input.css({'width': 'auto'});
                }
            }
            
            // Year field
            const year_filter = report.get_filter('expiry_year');
            if (year_filter && year_filter.$wrapper) {
                const year_label = year_filter.$wrapper.find('.control-label');
                const year_input = year_filter.$wrapper.find('.form-control');
                
                if (year_label.length && year_input.length) {
                    year_filter.$wrapper.css({
                        'display': 'flex',
                        'align-items': 'center',
                        'gap': '8px'
                    });
                    
                    year_label.css({
                        'width': 'auto',
                        'min-width': '50px',
                        'margin': '0',
                        'padding': '0',
                        'font-weight': '500',
                        'flex-shrink': '0'
                    });
                    
                    year_input.parent().css({
                        'flex': '1',
                        'display': 'inline-block'
                    });
                    year_input.css({'width': 'auto'});
                }
            }
            
            console.log('✅ Month/Year labels forced outside fields');
        }, 2000);


    
        // Intercept report refresh - only allow manual "Show Report" button
        setTimeout(function() {
            const original_refresh = report.refresh.bind(report);
            let allow_refresh = false;
            
            // Override refresh function
            report.refresh = function() {
                if (allow_refresh) {
                    allow_refresh = false;
                    original_refresh();
                } else {
                    console.log('⚠️ Auto-refresh blocked. Use Show Report button.');
                }
            };
            
            // Make "Show Report" button work
            $(document).on('click', '#show-report-btn-amc', function() {
                allow_refresh = true;
                report.refresh();
            });
            
            // Allow page load refresh (first time)
            allow_refresh = true;
            setTimeout(function() {
                allow_refresh = false;
            }, 2000);
            
            console.log('Report refresh now controlled by Show Report button only');
        }, 1200);
        
        // ⭐ SEARCH BUTTON (same level as filters)
        setTimeout(function() {
            const customer_wrapper = report.page.fields_dict.customer_name.$wrapper;
            
            if (customer_wrapper && !$('#customer-search-btn-wrapper').length) {
                const search_button_wrapper = $(`
                    <div id="customer-search-btn-wrapper" class="frappe-control" 
                        style="display: inline-block !important; 
                                vertical-align: top !important; 
                                margin-left: 8px !important;
                                margin-top: 1px !important;
                                line-height: 1 !important;">
                        <div class="form-group" style="margin-bottom: 0 !important;">
                            <div class="control-input-wrapper">
                                <button class="btn btn-default btn-sm" 
                                        id="customer-search-btn-amc"
                                        style="height: 25px !important;
                                            width: 120px !important;
                                            line-height: 1.3 !important;
                                            padding: 0 12px !important;
                                            margin: 0 !important;
                                            position: relative !important;
                                            top: 1px !important;
                                            background: #000 !important; 
                                            color: #fff !important; 
                                            border: 1px solid #000 !important;
                                            border-radius: 4px !important;
                                            font-size: 12px !important;
                                            font-weight: 500 !important;
                                            display: flex !important;
                                            align-items: center !important;
                                            justify-content: center !important;
                                            gap: 4px !important;
                                            cursor: pointer !important;">
                                    <svg style="width: 12px; height: 12px;" 
                                        xmlns="http://www.w3.org/2000/svg" 
                                        viewBox="0 0 24 24" 
                                        fill="none" 
                                        stroke="currentColor" 
                                        stroke-width="2.5">
                                        <circle cx="11" cy="11" r="8"></circle>
                                        <path d="m21 21-4.35-4.35"></path>
                                    </svg>
                                    <span>Search</span>
                                </button>
                            </div>
                        </div>
                    </div>
                `);
                
                customer_wrapper.after(search_button_wrapper);
                
                $('#customer-search-btn-amc').on('click', function(e) {
                    e.preventDefault();
                    show_customer_search_popup(report);
                });
                
                $('#customer-search-btn-amc').hover(
                    function() { $(this).css({'background': '#333'}); },
                    function() { $(this).css({'background': '#000'}); }
                );
            }
        }, 300);
        
        // ⭐ HIDE COLUMN FILTER SEARCH BOXES
        function hide_column_filters() {
            $('.dt-row-filter').hide();
            $('.dt-filter').hide();
            $('.dt-inline-search').hide();
            $('.dt-cell--header input').hide();
            $('.dt-cell--header .form-control').hide();
            $('.data-table input[type="text"]').hide();
        }
        
        setTimeout(hide_column_filters, 100);
        setTimeout(hide_column_filters, 500);
        setTimeout(hide_column_filters, 1000);
        
        const originalRefresh = report.refresh.bind(report);
        report.refresh = function() {
            originalRefresh();
            setTimeout(hide_column_filters, 100);
        };

        // ⭐ SHOW REPORT BUTTON
        setTimeout(function() {
            if (!$('#show-report-btn-amc').length) {
                const show_report_btn = $(`
                    <button class="btn btn-primary btn-sm" 
                            id="show-report-btn-amc"
                            style="margin-right: 8px; 
                                padding: 6px 16px;
                                font-size: 13px;
                                font-weight: 500;
                                border-radius: 4px;
                                background: #000000ff !important;
                                border: 1px solid #000000ff !important;
                                color: #fff !important;
                                cursor: pointer !important;">
                        Show Report
                    </button>
                `);
                
                $('.page-head-content .standard-actions').prepend(show_report_btn);
                
                $('#show-report-btn-amc').on('click', function(e) {
                    e.preventDefault();
                    report.refresh();
                });
                
                $('#show-report-btn-amc').hover(
                    function() { $(this).css({'background': '#333'}); },
                    function() { $(this).css({'background': '#000000ff'}); }
                );
            }
        }, 300);
    }
};

// ⭐ CUSTOMER SEARCH POPUP
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
                report.set_filter_value('customer_name', selected_customer.name);
                dialog.hide();
            } else {
                frappe.msgprint(__('Please select a customer'));
            }
        }
    });
    
    dialog.fields_dict.search_input.$input.on('input', function() {
        const query = $(this).val().trim();
        
        if (debounce_timer) clearTimeout(debounce_timer);
        
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
            args: { search_term: query },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    search_results = r.message;
                    render_results();
                } else {
                    show_no_results();
                }
            },
            error: function() {
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
        
        $('.customer-item').on('click', function() {
            const idx = $(this).data('idx');
            selected_customer = search_results[idx];
            render_results();
        });
        
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

// ⭐ MOBILE RESPONSIVE STYLES
function add_mobile_styles() {
    if (!$('#custom-report-mobile-styles').length) {
        $('head').append(`
            <style id="custom-report-mobile-styles">
                /* ===== HIDE COLUMN FILTER SEARCH BOXES ===== */
                .dt-inline-search,
                .dt-cell--header input,
                .dt-cell--header input[type="text"],
                .dt-filter,
                .dt-filter-input,
                .dt-row-filter,
                .dt-cell--header .form-control,
                .data-table input[type="text"] {
                    display: none !important;
                    visibility: hidden !important;
                    height: 0 !important;
                    width: 0 !important;
                    padding: 0 !important;
                    margin: 0 !important;
                    border: none !important;
                }

                /* ⭐ FORCE MONTH/YEAR TO COMPLETELY NEW ROW */
                .frappe-control[data-fieldname="expiry_month"] {
                    clear: both !important;
                    display: block !important;
                    width: 100% !important;
                    margin-top: 10px !important;
                    float: none !important;
                }
                
                .frappe-control[data-fieldname="expiry_month"].show-filter {
                    display: block !important;
                }
                
                .frappe-control[data-fieldname="expiry_year"] {
                    display: inline-block !important;
                    margin-left: 0px !important;
                    margin-top: 10px !important;
                    float: none !important;
                }
                
                .frappe-control[data-fieldname="expiry_year"].show-filter {
                    display: inline-block !important;
                }

                /* ⭐ DEFAULT HIDE - Complete removal from flow */
                .frappe-control[data-fieldname="expiry_month"]:not(.show-filter),
                .frappe-control[data-fieldname="expiry_year"]:not(.show-filter) {
                    display: none !important;
                    visibility: hidden !important;
                    opacity: 0 !important;
                    height: 0 !important;
                    width: 0 !important;
                    overflow: hidden !important;
                    position: absolute !important;
                    left: -9999px !important;
                }
                
                /* ⭐ KEEP FIRST ROW INLINE */
                .frappe-control[data-fieldname="customer_name"],
                .frappe-control[data-fieldname="amc_status"],
                #customer-search-btn-wrapper {
                    display: inline-block !important;
                    vertical-align: top !important;
                    float: none !important;
                }

                /* ⭐ PLACEHOLDER EFFECT - Hide label when field has value */
                .frappe-control[data-fieldname="expiry_month"] label.control-label,
                .frappe-control[data-fieldname="expiry_year"] label.control-label {
                    transition: opacity 0.2s ease !important;
                }

                .frappe-control[data-fieldname="expiry_month"] label.control-label.hidden,
                .frappe-control[data-fieldname="expiry_year"] label.control-label.hidden {
                    display: none !important;
                }
                
                /* ===== MOBILE RESPONSIVE STYLES ===== */
                
                @media (max-width: 768px) {
                    .report-wrapper {
                        overflow-x: auto !important;
                        -webkit-overflow-scrolling: touch !important;
                        width: 100% !important;
                    }
                    
                    .report-wrapper .datatable {
                        font-size: 12px !important;
                        width: max-content !important;
                        min-width: 100% !important;
                    }
                    
                    .report-wrapper .datatable .dt-cell__content {
                        white-space: nowrap !important;
                        overflow: hidden !important;
                        text-overflow: ellipsis !important;
                        padding: 8px !important;
                    }
                    
                    .report-wrapper .datatable .dt-scrollable {
                        overflow-x: auto !important;
                        overflow-y: auto !important;
                        width: 100% !important;
                    }
                    
                    .report-wrapper .datatable .dt-cell,
                    .report-wrapper .datatable .dt-cell--header {
                        min-width: 100px !important;
                        max-width: none !important;
                    }
                    
                    .report-wrapper .datatable .dt-cell[data-col-index="0"],
                    .report-wrapper .datatable .dt-cell--header[data-col-index="0"] {
                        min-width: 130px !important;
                        width: 130px !important;
                    }
                    
                    .report-wrapper .datatable .dt-cell[data-col-index="1"],
                    .report-wrapper .datatable .dt-cell--header[data-col-index="1"] {
                        min-width: 200px !important;
                        width: 200px !important;
                    }
                    
                    .report-wrapper .datatable .dt-cell[data-col-index="2"],
                    .report-wrapper .datatable .dt-cell--header[data-col-index="2"] {
                        min-width: 130px !important;
                        width: 130px !important;
                    }
                    
                    .report-wrapper .datatable .dt-cell[data-col-index="3"],
                    .report-wrapper .datatable .dt-cell--header[data-col-index="3"] {
                        min-width: 220px !important;
                        width: 220px !important;
                    }
                    
                    .report-wrapper .datatable .dt-cell[data-col-index="4"],
                    .report-wrapper .datatable .dt-cell--header[data-col-index="4"] {
                        min-width: 130px !important;
                        width: 130px !important;
                    }
                    
                    .report-wrapper .datatable .dt-cell[data-col-index="5"],
                    .report-wrapper .datatable .dt-cell--header[data-col-index="5"] {
                        min-width: 140px !important;
                        width: 140px !important;
                    }
                    
                    .report-wrapper .datatable .dt-cell--header {
                        font-weight: 600 !important;
                        background: #f8f9fa !important;
                        border-bottom: 2px solid #dee2e6 !important;
                        text-align: left !important;
                        vertical-align: middle !important;
                    }
                    
                    .report-wrapper .datatable .dt-cell {
                        vertical-align: middle !important;
                        text-align: left !important;
                        border-bottom: 1px solid #e9ecef !important;
                    }
                    
                    .report-wrapper .datatable .dt-row:hover {
                        background-color: #f8f9fa !important;
                    }
                }
                
                @media (max-width: 576px) {
                    .report-wrapper .datatable {
                        font-size: 11px !important;
                    }
                    
                    .report-wrapper .datatable .dt-cell__content {
                        padding: 6px !important;
                    }
                }
            </style>
        `);
    }
}

