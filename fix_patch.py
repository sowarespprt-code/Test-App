import re
with open('/home/user/test-bench/apps/test_app/test_app/frontend_overrides/helpdesk_ui.patch', 'r') as f:
    content = f.read()

# 1. Update virtualFields
content = content.replace(
"""+const virtualFields = ref({
+  custom_customercode: "",
+  custom_product: "",
+  custom_popup_messages: "",
+  custom_remarks: "",
+  custom_amc_end_date: "",
+  custom_amc_status: "",
+});""",
"""+const virtualFields = ref({
+  custom_customercode: "",
+  custom_product: "",
+  custom_popup_messages: "",
+  custom_remarks: "",
+  custom_amc_end_date: "",
+  custom_amc_status: "",
+  custom_contactperson: "",
+  custom_phone_number: "",
+});""")

# 2. Fix setValue.submit
content = content.replace(
"""+    // ✅ Safe save - no get/reload needed
+    await ticket.value.setValue.submit({
+      customer: customerId,
+      custom_customer_name: customerName
+    });""",
"""+    // ✅ Safe save - no get/reload needed
+    await ticket.value.setValue.submit({
+      customer: customerId
+    });""")

content = content.replace(
"""+      // Retry memory + save
+      ticket.value.doc.customer = customerId;
+      ticket.value.doc.custom_customer_name = customerName;
+      await ticket.value.setValue.submit({
+        customer: customerId,
+        custom_customer_name: customerName
+      });""",
"""+      // Retry memory + save
+      ticket.value.doc.customer = customerId;
+      ticket.value.doc.custom_customer_name = customerName;
+      await ticket.value.setValue.submit({
+        customer: customerId
+      });""")

# 3. Update get_list fields (2 occurrences)
content = content.replace(
"""+      fields: [
+        "name",
+        "customer_name", 
+        "custom_customercode", 
+        "custom_productname", 
+        "custom_remarks"
+      ],""",
"""+      fields: [
+        "name",
+        "customer_name", 
+        "custom_customercode", 
+        "custom_productname", 
+        "custom_remarks",
+        "custom_contactperson",
+        "custom_phone001"
+      ],""")

content = content.replace(
"""+        fields: [
+          "name",
+          "customer_name",
+          "custom_customercode",
+          "custom_productname",
+          "custom_remarks"
+        ],""",
"""+        fields: [
+          "name",
+          "customer_name",
+          "custom_customercode",
+          "custom_productname",
+          "custom_remarks",
+          "custom_contactperson",
+          "custom_phone001"
+        ],""")

# 4. Update populateCustomerData
content = content.replace(
"""+  // ✅ Update virtual fields
+  virtualFields.value.custom_customercode = customer.custom_customercode || "";
+  virtualFields.value.custom_product = customer.custom_productname || "";
+  virtualFields.value.custom_remarks = customer.custom_remarks || "";
+
+  // ✅ Update ticket document (in memory only)
+  ticket.value.doc.custom_customercode = virtualFields.value.custom_customercode;
+  ticket.value.doc.custom_remarks = virtualFields.value.custom_remarks;""",
"""+  // ✅ Update virtual fields
+  virtualFields.value.custom_customercode = customer.custom_customercode || "";
+  virtualFields.value.custom_product = customer.custom_productname || "";
+  virtualFields.value.custom_remarks = customer.custom_remarks || "";
+  virtualFields.value.custom_contactperson = customer.custom_contactperson || "";
+  virtualFields.value.custom_phone_number = customer.custom_phone001 || "";
+
+  // ✅ Update ticket document (in memory only)
+  ticket.value.doc.custom_customercode = virtualFields.value.custom_customercode;
+  ticket.value.doc.custom_remarks = virtualFields.value.custom_remarks;
+  ticket.value.doc.custom_contactperson = virtualFields.value.custom_contactperson;
+  ticket.value.doc.custom_phone_number = virtualFields.value.custom_phone_number;""")

with open('/home/user/test-bench/apps/test_app/test_app/frontend_overrides/helpdesk_ui.patch', 'w') as f:
    f.write(content)
print("Patch updated!")
