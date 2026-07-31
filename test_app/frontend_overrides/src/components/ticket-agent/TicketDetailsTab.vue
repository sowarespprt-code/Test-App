<template>
  <div
    class="h-full overflow-y-hidden flex flex-1 flex-col justify-between overflow-hidden max-h-full"
  >
    <!-- ✅ Popup Components -->
    <CustomerSearchPopup 
      v-model="showCustomerSearchPopup" 
      @customer-selected="handleCustomerSelected" 
    />
    <LicenseDetailsPopup 
      v-model="showLicensePopup" 
      :customer-code="virtualFields.custom_customercode" 
      @license-loaded="handleLicenseLoaded" 
    />

    <div class="px-5 pb-4 flex flex-col">
      <!-- User avatar with buttons -->
      <TicketContact />
      <!-- Core Fields -->
      <div>
        <div
          v-for="(section, index) in coreFields"
          :key="index"
          :class="
            section.group ? 'flex gap-2 items-center w-full mb-3' : 'mb-3'
          "
        >
          <template v-for="field in section.fields">
            <Link
              v-if="field.visible"
              :key="field.fieldname"
              class="form-control-core"
              :class="section.group ? 'flex-1' : 'w-full'"
              :page-length="10"
              :label="field.label"
              :placeholder="field.placeholder"
              :doctype="field.doctype"
              :modelValue="field.value"
              :required="field.required"
              @update:model-value="
              (val:string) => handleFieldUpdate(field.fieldname, val,true)
            "
            />
          </template>
        </div>

        <!-- Assignee component -->
        <AssignTo />
      </div>
    </div>

    <!-- Additional Fields -->
    <div class="border-t flex flex-col flex-1 h-full pb-3 overflow-y-hidden">
      <div class="overflow-y-scroll max-h-[80%]">
        <!-- ✅ BUTTONS ROW (Above Customer Code) -->
        <div class="px-5 pt-3 pb-2">
          <div class="flex gap-2">
            <!-- Customer Search Button -->
            <button
              class="inline-flex items-center gap-1 px-3 py-1.5 text-xs bg-blue-500 hover:bg-blue-600 text-white font-medium rounded transition-colors duration-200 shadow-sm"
              @click="openCustomerSearchPopup"
              title="Search Customer Details"
              type="button"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.35-4.35"></path>
              </svg>
              <span>Search Customer</span>
            </button>
            
            <!-- License Button -->
            <button
              class="inline-flex items-center gap-1 px-3 py-1.5 text-xs bg-green-500 hover:bg-green-600 text-white font-medium rounded transition-colors duration-200 shadow-sm"
              @click="openLicensePopup"
              title="View License Details"
              type="button"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
              </svg>
              <span>View License</span>
            </button>
          </div>
        </div>

        <!-- All Custom Fields (Normal rendering) -->
        <template v-for="field in customFields">
          <TicketField
            v-if="field.visible"
            :key="field.fieldname"
            :field="field"
            :value="getFieldValueWithVirtual(field.fieldname)"
            @change="
              ({ fieldname, value }) => handleFieldUpdate(fieldname, value)
            "
          />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Link } from "@/components";
import { parseField } from "@/composables/formCustomisation";
import { useNotifyTicketUpdate } from "@/composables/realtime";
import { getMeta } from "@/stores/meta";
import {
  AssigneeSymbol,
  CustomizationSymbol,
  FieldValue,
  TicketSymbol,
} from "@/types";
import { computed, inject, ref, watch, onMounted, nextTick } from "vue";
import TicketField from "../TicketField.vue";
import AssignTo from "./AssignTo.vue";
import TicketContact from "./TicketContact.vue";
import { call } from "frappe-ui";
import CustomerSearchPopup from "@/components/CustomerSearchPopup.vue";
import LicenseDetailsPopup from "@/components/LicenseDetailsPopup.vue";

const ticket = inject(TicketSymbol);
const assignees = inject(AssigneeSymbol);
const customizations = inject(CustomizationSymbol);
const { getFields, getField } = getMeta("HD Ticket");
const { notifyTicketUpdate } = useNotifyTicketUpdate(ticket.value?.name);
const licenseData = ref<any | null>(null);
const licenseLoading = ref(false);
const amcSnapshot = ref<{ AMCEndDate: string | null; status: string | null } | null>(null);

const showCustomerSearchPopup = ref(false);
const showLicensePopup = ref(false);

const virtualFields = ref({
  custom_customercode: "",
  custom_product: "",
  custom_popup_messages: "",
  custom_remarks: "",
  custom_amc_end_date: "",
  custom_amc_status: "",
});

const lastProcessedCustomer = ref("");

function openCustomerSearchPopup() {
  console.log("[DETAILS TAB] 🔍 Opening customer search popup");
  showCustomerSearchPopup.value = true;
}


// ✅ SINGLE shared function for all customer change paths (popup + dropdown)
async function applyCustomerChange(customer: any) {
  console.log("[DETAILS TAB] 👤 Applying customer change:", customer);

  if (!customer || !customer.name) {
    console.warn("[DETAILS TAB] ⚠️ Invalid customer data");
    return;
  }

  const customerId     = customer.name;
  const customerName   = customer.customer_name || "";
  const customerCode   = customer.custom_customercode || "";
  const customerProduct = customer.custom_productname || "";

  // ① Lock watcher so it doesn't re-trigger on our own save
  lastProcessedCustomer.value = customerId;

  // ② Update local doc memory immediately so UI refreshes
  ticket.value.doc.customer             = customerId;
  ticket.value.doc.custom_customer_name = customerName;
  ticket.value.doc.custom_customercode  = customerCode;

  // ③ Update virtual display fields immediately
  virtualFields.value.custom_customercode = customerCode;
  virtualFields.value.custom_product      = customerProduct;
  virtualFields.value.custom_remarks      = customer.custom_remarks || "";

  // ④ Persist to server in ONE atomic call with all fields
  //    This prevents the Server Script "To Fill customer Name" from reverting us
  try {
    await ticket.value.setValue.submit({
      customer:              customerId,
      custom_customer_name:  customerName,
      custom_customercode:   customerCode,
      custom_product:        customerProduct,
    });
    
    // ✅ RELOAD from DB to fetch all the other fields (product, team, contact, phone) 
    // that were automatically populated by the Server Script "To Fill customer Name"
    await ticket.value.reload();
    console.log("[DETAILS TAB] 💾 Saved customer & fetched server-populated fields:", customerId);
  } catch (error: any) {
    if (error._server_messages?.[0]?.includes("TimestampMismatchError")) {
      // Reload once then retry
      await ticket.value.reload();
      lastProcessedCustomer.value = customerId;
      ticket.value.doc.customer             = customerId;
      ticket.value.doc.custom_customer_name = customerName;
      ticket.value.doc.custom_customercode  = customerCode;
      await ticket.value.setValue.submit({
        customer:             customerId,
        custom_customer_name: customerName,
        custom_customercode:  customerCode,
        custom_product:       customerProduct,
      });
    } else {
      console.error("[DETAILS TAB] ❌ Save error:", error);
      throw error;
    }
  }

  // ⑤ After save completes, load AMC/popup alerts without a full reload
  await fetchLicenseDataForTicket();
  await fetchCustomerAlerts(customerId, customerCode);

  // ⑥ Refresh assignees
  if (assignees?.value) {
    assignees.value.reload();
  }

  console.log("[DETAILS TAB] ✅ Customer change complete");
}

// Called from CustomerSearchPopup
async function handleCustomerSelected(customer: any) {
  await applyCustomerChange(customer);
}



async function openLicensePopup() {
  const code = virtualFields.value.custom_customercode?.trim();
  
  if (!code) {
    alert("Please select a customer first to view license details.");
    return;
  }

  if (code.length < 3) {
    alert("Customer Code must be at least 3 characters.");
    return;
  }

  console.log("[DETAILS TAB] 🔓 Opening license popup for code:", code);
  showLicensePopup.value = true;
  await fetchLicenseDataForTicket();
}

function handleLicenseLoaded(data: any) {
  console.log("[DETAILS TAB] 📦 License data loaded:", data);
  licenseData.value = data;
}


// ✅ SIMPLIFIED: loadVirtualFields - no more saves
async function loadVirtualFields() {
  const customerId = ticket?.value?.doc?.customer;
  const customerNameField = ticket?.value?.doc?.custom_customer_name;
  const ticketName = ticket?.value?.doc?.name;
  
  console.log("[DETAILS TAB] 📥 Loading virtual fields with:", {
    customerId,
    customerNameField,
    ticketName
  });
  
  if (!customerId && !customerNameField) {
    console.log("[DETAILS TAB] ⚠️ No customer information available");
    clearVirtualFields();
    return;
  }

  const lookupValue = customerId || customerNameField;
  console.log("[DETAILS TAB] 📥 Fetching HD Customer:", lookupValue);
  lastProcessedCustomer.value = lookupValue;

  try {
    // ✅ Try by ID first
    let result = await call("frappe.client.get_list", {
      doctype: "HD Customer",
      filters: { name: lookupValue },
      fields: [
        "name",
        "customer_name", 
        "custom_customercode", 
        "custom_productname", 
        "custom_remarks"
      ],
      limit: 1
    });

    console.log("[DETAILS TAB] ✅ HD Customer lookup by ID:", result);
    
    // ✅ Fallback to customer_name if needed
    if (!result || result.length === 0) {
      console.log("[DETAILS TAB] 🔍 Trying lookup by customer_name...");
      
      result = await call("frappe.client.get_list", {
        doctype: "HD Customer",
        filters: { customer_name: lookupValue },
        fields: [
          "name",
          "customer_name",
          "custom_customercode",
          "custom_productname",
          "custom_remarks"
        ],
        limit: 1
      });
      
      console.log("[DETAILS TAB] ✅ HD Customer lookup by name:", result);
    }
    
    if (result && result.length > 0) {
      const customer = result[0];
      await populateCustomerData(customer, ticketName);
    } else {
      console.log("[DETAILS TAB] ❌ Customer not found");
      clearVirtualFields();
    }

  } catch (error) {
    console.error("[DETAILS TAB] ❌ Virtual fields error:", error);
    clearVirtualFields();
  }
}

// ✅ FIXED: Remove the save attempt from populateCustomerData
async function populateCustomerData(customer: any, ticketName: string) {
  console.log("[DETAILS TAB] 📝 Populating data from customer:", customer);
  
  // ✅ Update virtual fields
  virtualFields.value.custom_customercode = customer.custom_customercode || "";
  virtualFields.value.custom_product = customer.custom_productname || "";
  virtualFields.value.custom_remarks = customer.custom_remarks || "";

  // ✅ Update ticket document (in memory only)
  ticket.value.doc.custom_customercode = virtualFields.value.custom_customercode;
  ticket.value.doc.custom_remarks = virtualFields.value.custom_remarks;
  
  // ✅ Update custom_customer_name in memory (NO SAVE)
  const currentCustomerName = ticket.value.doc.custom_customer_name;
  if (!currentCustomerName || currentCustomerName.length < 10 || currentCustomerName === customer.name) {
    console.log("[DETAILS TAB] 🔧 Updating custom_customer_name in memory to:", customer.customer_name);
    ticket.value.doc.custom_customer_name = customer.customer_name;
    // ❌ REMOVED: Don't save here - it causes timestamp mismatch
  }

  // ✅ Fetch license data if customer code exists
  if (virtualFields.value.custom_customercode) {
    console.log("[DETAILS TAB] 🚀 Triggering AMC for code:", virtualFields.value.custom_customercode);
    await fetchLicenseDataForTicket();
  }

  // ✅ Load customer alerts
  if (ticketName && !ticket.value.doc.__islocal) {
    const storageKey = `ticket_popup_${ticketName}`;
    const storedPopupMessages = localStorage.getItem(storageKey);
    if (storedPopupMessages) {
      virtualFields.value.custom_popup_messages = storedPopupMessages;
    } else {
      await fetchCustomerAlerts(customer.name, virtualFields.value.custom_customercode);
    }
  } else {
    await fetchCustomerAlerts(customer.name, virtualFields.value.custom_customercode);
  }

  console.log("[DETAILS TAB] ✅ Virtual fields loaded:", virtualFields.value);
}

function clearVirtualFields() {
  virtualFields.value = {
    custom_customercode: "",
    custom_product: "",
    custom_popup_messages: "",
    custom_remarks: "",
    custom_amc_end_date: "",
    custom_amc_status: "",
  };
  ticket.value.doc.custom_customercode = "";
  ticket.value.doc.custom_remarks = "";
  licenseData.value = null;
  amcSnapshot.value = null;
}

async function fetchCustomerAlerts(customerName: string, customerCode?: string) {
  try {
    const code = customerCode || virtualFields.value.custom_customercode;
    let result: any[] = [];
    
    if (code) {
      result = await call('frappe.client.get_list', {
        doctype: 'Customer Alert',
        filters: { customer_code: code },
        fields: ['name', 'popupmessage', 'modified'],
        order_by: 'modified desc',
        limit: 10
      });
    }
    
    if (!result || result.length === 0) {
      result = await call('frappe.client.get_list', {
        doctype: 'Customer Alert',
        filters: { customer_name: customerName },
        fields: ['name', 'popupmessage', 'modified'],
        order_by: 'modified desc',
        limit: 10
      });
    }
    
    if (result && result.length > 0) {
      virtualFields.value.custom_popup_messages = result
        .map(a => a.popupmessage)
        .filter(msg => msg)
        .join('\n\n') || '';
      console.log("[DETAILS TAB] ✅ Popup messages loaded");
    } else {
      virtualFields.value.custom_popup_messages = '';
    }
  } catch (error) {
    console.error('[DETAILS TAB] ❌ Customer alerts error:', error);
    virtualFields.value.custom_popup_messages = '';
  }
}

async function fetchLicenseDataForTicket() {
  const customerCode = (ticket.value?.doc?.custom_customercode || virtualFields.value.custom_customercode)?.trim();

  console.log("[DETAILS TAB] 📡 License fetch for code:", customerCode);

  if (!customerCode || customerCode.length < 3) {
    console.log("[DETAILS TAB] ⚠️ Invalid customer code");
    licenseData.value = null;
    return;
  }

  licenseLoading.value = true;

  try {
    console.log("[DETAILS TAB] 🔗 Calling license API...");
    const apiResult = await call("helpdesk.api.license.get_customer_license_details", {
      customer_code: customerCode,
    });

    licenseData.value = apiResult || null;
    console.log("[DETAILS TAB] 📦 API result:", apiResult);

    if (!licenseData.value?.AMCEndDate || String(licenseData.value.AMCEndDate) === "null") {
      console.log("[DETAILS TAB] ⚠️ No AMC in API → HD Customer");
      const fallbackDate = await fetchAmcFromCustomer(customerCode);
      if (fallbackDate) {
        licenseData.value = {
          ...licenseData.value,
          AMCEndDate: fallbackDate,
          source: "HD Customer",
        };
        console.log("[DETAILS TAB] ✅ HD Customer AMC:", fallbackDate);
      } else {
        licenseData.value = null;
      }
    } else {
      licenseData.value.source = "API";
    }

  } catch (apiError) {
    console.log("[DETAILS TAB] ❌ API failed → HD Customer fallback");
    const fallbackDate = await fetchAmcFromCustomer(customerCode);
    if (fallbackDate) {
      licenseData.value = {
        AMCEndDate: fallbackDate,
        source: "HD Customer (API failed)",
      };
    } else {
      licenseData.value = null;
    }
  } finally {
    licenseLoading.value = false;
  }
}

async function fetchAmcFromCustomer(customerCode: string) {
  if (!customerCode || customerCode.length < 3) return null;

  const cleanCode = customerCode.trim();
  console.log("[DETAILS TAB] 🗄️ HD Customer lookup for:", cleanCode);

  try {
    let result = await call("frappe.client.get_list", {
      doctype: "HD Customer",
      filters: { custom_customercode: cleanCode },
      fields: ["name", "custom_customercode", "custom_dateofamclastpaid"],
      limit: 1
    });

    if (!result || result.length === 0) {
      console.log("[DETAILS TAB] 🔍 Trying partial match...");
      result = await call("frappe.client.get_list", {
        doctype: "HD Customer",
        filters: { custom_customercode: ["like", `%${cleanCode}%`] },
        fields: ["name", "custom_customercode", "custom_dateofamclastpaid"],
        limit: 3
      });
    }

    console.log("[DETAILS TAB] 🗄️ HD Customer results:", result);

    if (result && result.length > 0) {
      const raw = result[0].custom_dateofamclastpaid;
      const cleanDate = (raw && String(raw).trim()) ? String(raw).trim() : null;
      console.log("[DETAILS TAB] ✅ AMC FOUND:", cleanDate);
      return cleanDate;
    }

    console.log("[DETAILS TAB] ℹ️ No HD Customer match");
    return null;

  } catch (error) {
    console.error("[DETAILS TAB] ❌ HD Customer error:", error);
    return null;
  }
}

function loadAmcSnapshotFromStorage() {
  const ticketName = ticket.value?.doc?.name;
  if (!ticketName || ticket.value.doc.__islocal) return;

  const raw = localStorage.getItem(`ticket_amc_${ticketName}`);
  if (!raw) return;

  try {
    amcSnapshot.value = JSON.parse(raw);
    console.log("[DETAILS TAB] ✅ AMC snapshot loaded");
  } catch (e) {
    console.error("[DETAILS TAB] ❌ Snapshot parse error:", e);
  }
}

const formattedAmcEndDate = computed(() => {
  const snapDate = amcSnapshot.value?.AMCEndDate;
  if (snapDate) return formatAmcDate(String(snapDate));

  if (licenseLoading.value) return "Loading...";
  if (!licenseData.value?.AMCEndDate) return "N/A";
  return formatAmcDate(String(licenseData.value.AMCEndDate));
});

const amcStatusText = computed(() => {
  const snapStatus = amcSnapshot.value?.status;
  if (snapStatus) return String(snapStatus);

  if (licenseLoading.value) return "Loading...";
  if (!licenseData.value?.AMCEndDate) return "Unknown";
  return deriveAmcStatus(String(licenseData.value.AMCEndDate));
});

const amcStatusClass = computed(() => {
  if (licenseLoading.value) {
    return "bg-gray-100 text-gray-600 border border-gray-300";
  }
  const status = amcStatusText.value;
  if (status === "Expired") return "bg-red-100 text-red-800 border border-red-300";
  if (status === "Active") return "bg-green-100 text-green-800 border border-green-300";
  return "bg-gray-100 text-gray-800 border border-gray-300";
});

function formatAmcDate(rawInput: string): string {
  const raw = String(rawInput || "").trim();
  if (!raw || raw === "null" || raw === "undefined") return "N/A";

  if (raw.includes("/")) {
    const datePart = raw.split(" ")[0];
    const parts = datePart.split("/");
    if (parts.length === 3) {
      const day = parseInt(parts[0], 10);
      const month = parseInt(parts[1], 10);
      const year = parseInt(parts[2], 10);
      if (!isNaN(day) && !isNaN(month) && !isNaN(year)) {
        const d = new Date(year, month - 1, day);
        if (!isNaN(d.getTime())) {
          return d.toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
          });
        }
      }
    }
  }

  const d = new Date(raw);
  if (!isNaN(d.getTime())) {
    return d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }

  return "Invalid Date";
}

function deriveAmcStatus(rawInput: string): string {
  const raw = String(rawInput || "").trim();
  if (!raw || raw === "null" || raw === "undefined") return "Unknown";

  let endDate: Date | undefined;

  if (raw.includes("/")) {
    const datePart = raw.split(" ")[0];
    const parts = datePart.split("/");
    if (parts.length === 3) {
      const day = parseInt(parts[0], 10);
      const month = parseInt(parts[1], 10);
      const year = parseInt(parts[2], 10);
      if (!isNaN(day) && !isNaN(month) && !isNaN(year)) {
        endDate = new Date(year, month - 1, day);
      }
    }
  } else {
    endDate = new Date(raw);
  }

  if (!endDate || isNaN(endDate.getTime())) return "Unknown";

  const today = new Date();
  endDate.setHours(0, 0, 0, 0);
  today.setHours(0, 0, 0, 0);

  return endDate < today ? "Expired" : "Active";
}

async function reloadAllCustomerData() {
  console.log("[DETAILS TAB] 🔄 Reloading all customer data...");
  clearVirtualFields();
  await loadVirtualFields();
  loadAmcSnapshotFromStorage();
}

onMounted(async () => {
  console.log("[DETAILS TAB] 🎬 Component mounted");
  await nextTick();
  await reloadAllCustomerData();
});

// Single watcher: only fires when the ticket is first loaded (external changes)
// NOT for changes we make ourselves (lastProcessedCustomer guards against that)
watch(
  () => ticket?.value?.doc?.customer,
  async (newCustomerId, oldCustomerId) => {
    console.log("[DETAILS TAB] 👤 ticket.customer changed:", oldCustomerId, "→", newCustomerId);

    if (!newCustomerId) {
      clearVirtualFields();
      lastProcessedCustomer.value = "";
      return;
    }

    // Skip if WE just set this value (avoids reload loop)
    if (newCustomerId === lastProcessedCustomer.value) {
      console.log("[DETAILS TAB] ⏭️ Skipping watcher (self-triggered)");
      return;
    }

    // External change (e.g. initial load, or another tab saved)
    lastProcessedCustomer.value = newCustomerId;
    await nextTick();
    await reloadAllCustomerData();
  },
  { immediate: false }
);

watch(
  () => ticket?.value?.doc?.name,
  async (newTicketName) => {
    if (newTicketName && !ticket.value.doc.__islocal) {
      await nextTick();
      loadAmcSnapshotFromStorage();
    }
  },
  { immediate: false }
);

watch(
  () => licenseData.value?.AMCEndDate,
  (newVal) => {
    if (!newVal) {
      virtualFields.value.custom_amc_end_date = "";
      virtualFields.value.custom_amc_status = "";
      return;
    }
    virtualFields.value.custom_amc_end_date = String(newVal);
    virtualFields.value.custom_amc_status = amcStatusText.value;
    console.log("[DETAILS TAB] 💾 AMC virtual fields updated:", {
      end: virtualFields.value.custom_amc_end_date,
      status: virtualFields.value.custom_amc_status,
    });
  }
);



const coreFields = computed(() => {
  const fieldsMeta = getFields();
  if (!fieldsMeta || fieldsMeta.length === 0) return [];
  
  const _coreFields = [
    { group: true, fields: [getField("ticket_type"), getField("priority")] },
    { group: false, fields: [getField("customer")] },
    { group: true, fields: [getField("agent_group")] },
  ];

  _coreFields.forEach((section) => {
    section.fields = section.fields.map((f) => {
      let meta = parseField(f, ticket.value.doc);
      meta["required"] = meta.reqd;
      let field = getFieldInFormat(meta, meta);
      field["visible"] = true;

      // ✅ Force customer field to always show display name
      if (field.fieldname === "customer") {
        field.value = getCustomerDisplayValue();
      }

      return field;
    });
  });

  return _coreFields;
});




const customFields = computed(() => {
  const fieldsMeta = getFields();
  if (!fieldsMeta || fieldsMeta.length === 0) return [];

  if (!customizations.value.data || customizations.value.loading) return [];
  let customFields = customizations.value.data?.custom_fields || [];
  const _coreFields = [
    "ticket_type", "priority", "customer", "agent_group", "subject", "status",
  ];
  customFields = customFields.filter((f) => !_coreFields.includes(f.fieldname));
  
  return customFields.map((f) => {
    let fieldMeta = getField(f.fieldname);
    fieldMeta = parseField(fieldMeta, ticket.value.doc);
    fieldMeta["required"] = fieldMeta.reqd || f.required;
    return getFieldInFormat(f, fieldMeta);
  });
});

const isTicketCreated = computed(() => {
  return ticket.value?.doc?.name && !ticket.value.doc.__islocal;
});

function getFieldInFormat(fieldTemplate: any, fieldMeta: any) {
  const virtualReadonlyFields = [
    "custom_product", "custom_customercode", "custom_popup_messages",
    "custom_popupmessage", "custom_amc_end_date", "custom_amc_status", "custom_remarks"
  ];
  
  const isVirtualField = virtualReadonlyFields.includes(fieldTemplate.fieldname);
  const shouldBeReadonly = isVirtualField && isTicketCreated.value;

  return {
    label: fieldMeta?.label || fieldTemplate.fieldname,
    value: ticket.value.doc[fieldTemplate.fieldname],
    fieldtype: fieldMeta?.fieldtype,
    doctype: fieldMeta?.options || "",
    options: fieldMeta?.options || "",
    placeholder: fieldTemplate.placeholder || `Enter ${fieldMeta?.label || fieldTemplate.fieldname}`,
    readonly: Boolean(fieldMeta.readonly) || shouldBeReadonly,
    disabled: Boolean(fieldMeta.readonly) || shouldBeReadonly,
    url_method: fieldTemplate.url_method || "",
    fieldname: fieldTemplate.fieldname,
    required: fieldTemplate.required || fieldMeta?.required || false,
    visible: fieldMeta.display_via_depends_on && !fieldMeta.hidden,
  };
}

function getCustomerDisplayValue() {
  // Prefer the explicit display name field
  const nameFromCustom = ticket.value?.doc?.custom_customer_name;
  if (nameFromCustom && String(nameFromCustom).trim().length > 0) {
    return nameFromCustom;
  }

  // Fallback: use HD Customer document name if it looks like a name
  const customerId = ticket.value?.doc?.customer;
  if (!customerId) return "";

  // If ticket.customer already looks like a name (not hash-like), use it
  if (!/^[a-z0-9]{6,}$/.test(String(customerId))) {
    return customerId;
  }

  // Last fallback: whatever is there
  return customerId;
}


function getFieldValueWithVirtual(fieldname: string) {
  if (fieldname === "custom_popup_messages" || fieldname === "custom_popupmessage") {
    return virtualFields.value.custom_popup_messages;
  }
  if (fieldname === "custom_customercode") {
    return virtualFields.value.custom_customercode;
  }
  if (fieldname === "custom_product") {
    return virtualFields.value.custom_product;
  }
  if (fieldname === "custom_remarks") {
    return virtualFields.value.custom_remarks;
  }
  if (fieldname === "custom_amc_end_date") {
    return virtualFields.value.custom_amc_end_date || formattedAmcEndDate.value;
  }
  if (fieldname === "custom_amc_status") {
    return virtualFields.value.custom_amc_status || amcStatusText.value;
  }
  return ticket.value.doc[fieldname];
}

function handleFieldUpdate(fieldname: string, value: FieldValue, isCoreFieldUpdated = false) {
  // ✅ SPECIAL: Handle custom_customer_name Link field selection
  if (fieldname === "custom_customer_name" && value) {
    console.log("[DETAILS TAB] 🔄 custom_customer_name dropdown selected:", value);

    // Fetch full customer object then use the shared applyCustomerChange helper
    call("frappe.client.get_list", {
      doctype: "HD Customer",
      filters: { name: value },
      fields: ["name", "customer_name", "custom_productname", "custom_customercode", "custom_remarks"],
      limit: 1
    }).then(async (result) => {
      if (result?.[0]) {
        await applyCustomerChange(result[0]);
      } else {
        console.error("[DETAILS TAB] ❌ Customer not found:", value);
      }
    }).catch(err => {
      console.error("[DETAILS TAB] ❌ Lookup error:", err);
    });

    return; // Exit early - don't process as normal field
  }

  // Virtual fields check (keep custom_customer_name blocked for normal processing)
  const virtualFieldsList = [
    "custom_popup_messages", "custom_popupmessage", "custom_product", 
    "custom_customercode", "custom_amc_end_date", "custom_amc_status", "custom_remarks"
  ];
  
  if (virtualFieldsList.includes(fieldname)) {
    console.log(`[DETAILS TAB] ⛔ Virtual field blocked: ${fieldname}`);
    return;
  }

  // Rest of your existing code (unchanged)
  if (ticket.value.doc[fieldname] === value) return;
  
  if (isCoreFieldUpdated) {
    const label = getField(fieldname)?.label || fieldname;
    notifyTicketUpdate(label, value as string);
  }
  
  ticket.value.setValue.submit(
    { [fieldname]: value },
    {
      onSuccess: () => {
        if (fieldname === "agent_group") {
          assignees.value.reload();
        }
      },
    }
  );
}

</script>