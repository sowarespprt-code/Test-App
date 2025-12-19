<template>
  <div class="flex flex-col h-full">
    <!-- Header -->
    <div class="border-b px-5 py-4 flex items-center justify-between bg-white">
      <div class="flex items-center gap-4">
        <button
          @click="router.back()"
          class="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          title="Back to List"
        >
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
        </button>
        <h1 class="text-2xl font-semibold text-gray-900">New Customer Alert</h1>
      </div>
      <div class="flex items-center gap-3">
        <Button variant="subtle" @click="router.back()">Cancel</Button>
        <Button variant="solid" :loading="isSaving" @click="saveAlert">
          <template #prefix>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
          </template>
          Save Alert
        </Button>
      </div>
    </div>

    <!-- Form Content -->
    <div class="flex-1 overflow-y-auto bg-gray-50">
      <div class="max-w-4xl mx-auto p-8">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <div class="space-y-8">
            <!-- Customer Selection - Vertical Layout -->
            <div class="space-y-6">
              <!-- Customer Code Field - Full Width -->
              <div class="w-full">
                <label class="block text-sm font-semibold text-gray-700 mb-2">
                  Customer Code <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="newAlert.customer_code"
                  type="text"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  placeholder="Enter customer code"
                  @input="handleCustomerCodeInput"
                  @keydown.enter.prevent="handleCustomerCodeEnter"
                  @blur="handleCustomerCodeBlur"
                />
              </div>

              <!-- Customer Name Field with Search Button - Full Width -->
              <div class="w-full">
                <label class="block text-sm font-semibold text-gray-700 mb-2">
                  Customer Name <span class="text-red-500">*</span>
                </label>
                <div class="flex gap-3">
                  <div class="flex-1">
                    <Autocomplete
                      v-if="customerOptions.length > 0"
                      v-model="newAlert.customer_name"
                      :options="customerOptions"
                      placeholder="Select customer"
                      class="w-full"
                      @update:modelValue="val => handleCustomerNameChange(val)"
                      @update:query="searchCustomers"
                    />
                    <div v-else class="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm text-gray-400 bg-gray-50">
                      Enter customer code or use search button
                    </div>
                  </div>
                  <!-- Customer Search Button - REDUCED WIDTH -->
                  <button
                    class="inline-flex items-center gap-1 px-3.5 py-1.5 text-xs bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg transition-colors duration-200 shadow-sm whitespace-nowrap flex-shrink-0 h-[38px] min-w-[70px]"
                    type="button"
                    @click.stop.prevent="openCustomerSearchPopup"
                    title="Search Customer Details"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <circle cx="11" cy="11" r="8"></circle>
                      <path d="m21 21-4.35-4.35"></path>
                    </svg>
                    <span>Search</span>
                  </button>
                </div>
              </div>

              <!-- License Button - REDUCED LENGTH -->
              <div class="w-full">
                <button
                  class="max-w-[200px] mx-auto inline-flex items-center justify-center gap-1.5 px-4 py-2.5 text-sm bg-green-500 hover:bg-green-600 text-white font-medium rounded-lg transition-colors duration-200 shadow-sm"
                  type="button"
                  @click.stop.prevent="openLicensePopup"
                  title="View License Details"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                    <line x1="8" y1="21" x2="16" y2="21"></line>
                    <line x1="12" y1="17" x2="12" y2="21"></line>
                  </svg>
                  <span>License</span>
                </button>
              </div>
            </div>

            <!-- Popup Message Field - Full Width Large Textarea -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">
                Popup Message 
              </label>
              <textarea
                v-model="newAlert.popupmessage"
                rows="12"
                class="w-full rounded-lg border border-gray-300 px-4 py-4 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-vertical"
                placeholder="Enter detailed popup message for this customer alert..."
              ></textarea>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- CustomerSearchPopup -->
    <Teleport to="body">
      <CustomerSearchPopup
        v-if="showCustomerSearchPopup"
        v-model="showCustomerSearchPopup"
        @customerSelected="handleCustomerSelected"
      />
    </Teleport>

    <!-- License Details Popup -->
    <Teleport to="body">
      <LicenseDetailsPopup
        v-if="showLicensePopup"
        v-model="showLicensePopup"
        :customer-code="newAlert.customer_code"
      />
    </Teleport>
  </div>
</template>



<script setup lang="ts">
import { ref, reactive, nextTick } from "vue";
import { useRouter } from "vue-router";
import { call, Button, Autocomplete } from "frappe-ui";
import { globalStore } from "@/stores/globalStore";
import CustomerSearchPopup from "@/components/CustomerSearchPopup.vue";
import LicenseDetailsPopup from "@/components/LicenseDetailsPopup.vue";

const router = useRouter();
const { $dialog } = globalStore();

const customerOptions = ref<any[]>([]);
const isSaving = ref(false);
const newAlert = reactive({ customer_name: "", customer_code: "", popupmessage: "" });

// Customer Code State
const isFetchingCustomerName = ref(false);
const lastValidatedCustomerCode = ref("");
const MIN_CODE_LENGTH = 3;
const isUpdatingInternally = ref(false);
const isManuallySelectingCustomer = ref(false);
const showCustomerSearchPopup = ref(false);
const showLicensePopup = ref(false);

// Initialize customer search
searchCustomers("");

async function searchCustomers(query: string) {
  try {
    const filters = query ? { customer_name: ["like", `%${query}%`] } : {};
    const data = await call("frappe.client.get_list", {
      doctype: "HD Customer",
      fields: ["name", "customer_name", "custom_customercode"],
      filters,
      limit_page_length: 20,
      order_by: "customer_name asc",
    });
    customerOptions.value = data.map((c: any) => ({
      label: c.customer_name || c.name,
      value: c.name,
      code: c.custom_customercode || "",
    }));
  } catch (err) {
    console.error("Failed to fetch customers:", err);
    customerOptions.value = [];
  }
}

async function handleCustomerNameChange(selectedOption: any) {
  if (!selectedOption || !selectedOption.value) return;
  newAlert.customer_name = selectedOption.value;
  if (selectedOption.code) {
    newAlert.customer_code = selectedOption.code;
    lastValidatedCustomerCode.value = selectedOption.code;
  } else {
    await fetchCustomerCode(selectedOption.value);
  }
}

async function fetchCustomerCode(customerName: string) {
  try {
    const result = await call("frappe.client.get_value", {
      doctype: "HD Customer",
      filters: { name: customerName },
      fieldname: ["custom_customercode"],
    });
    const code = result?.message?.custom_customercode || result?.custom_customercode;
    if (code) {
      newAlert.customer_code = code;
      lastValidatedCustomerCode.value = code;
    }
  } catch (error) {
    console.error("Error fetching customer code:", error);
  }
}

function extractValue(payload: any): string {
  if (payload == null || payload === undefined) return "";
  if (typeof payload === "string" || typeof payload === "number") return String(payload).trim();
  if (typeof payload === "object" && "value" in payload) return String(payload.value || "").trim();
  if (typeof payload === "object" && payload.target && "value" in payload.target) return String(payload.target.value || "").trim();
  return "";
}

function safeSetField(fieldname: string, payload: any) {
  const value = extractValue(payload);
  if (newAlert[fieldname] !== value) {
    newAlert[fieldname] = value;
  }
}

function handleCustomerCodeInput(event: any) {
  const value = event.target?.value?.trim() || "";
  safeSetField("customer_code", value);
}

async function handleCustomerCodeEnter(event: any) {
  const enteredCode = event.target.value?.trim();
  const previousCode = lastValidatedCustomerCode.value?.trim();

  if (!enteredCode) {
    isUpdatingInternally.value = true;
    safeSetField("customer_name", "");
    lastValidatedCustomerCode.value = "";
    isUpdatingInternally.value = false;
    return;
  }

  if (enteredCode.length < MIN_CODE_LENGTH) {
    $dialog({ title: 'Invalid Customer Code', message: `Customer Code must be at least ${MIN_CODE_LENGTH} characters.` });
    return;
  }

  if (enteredCode === previousCode) {
    // Code already validated, just open license popup
    showLicensePopup.value = true;
    return;
  }

  safeSetField("customer_code", enteredCode);
  const found = await fetchCustomerName(enteredCode);
  if (found) {
    lastValidatedCustomerCode.value = enteredCode;
    // ✅ AUTO-OPEN LICENSE POPUP after successful validation
    showLicensePopup.value = true;
  } else {
    $dialog({ title: 'Invalid Customer Code', message: 'No customer found for this code. Please check and try again.' });
    isUpdatingInternally.value = true;
    safeSetField("customer_name", "");
    lastValidatedCustomerCode.value = "";
    isUpdatingInternally.value = false;
  }
}


function handleCustomerCodeBlur() {}

async function fetchCustomerName(customerCode: string) {
  if (!customerCode || isFetchingCustomerName.value) return false;
  isFetchingCustomerName.value = true;
  try {
    const result = await call("frappe.client.get_list", {
      doctype: "HD Customer",
      filters: { custom_customercode: customerCode },
      fields: ["name", "customer_name"],
      limit: 1,
    });
    if (result && result.length > 0) {
      const customer = result[0];
      isUpdatingInternally.value = true;
      await nextTick();
      safeSetField("customer_name", customer.name);
      isUpdatingInternally.value = false;
      return true;
    }
    return false;
  } catch (error) {
    console.error("Error fetching customer:", error);
    return false;
  } finally {
    isFetchingCustomerName.value = false;
  }
}

function openCustomerSearchPopup() {
  showCustomerSearchPopup.value = true;
}

function openLicensePopup() {
  if (!newAlert.customer_code || newAlert.customer_code.trim().length < MIN_CODE_LENGTH) {
    $dialog({ 
      title: 'Invalid Customer Code', 
      message: 'Please enter a valid customer code to view license details.' 
    });
    return;
  }
  showLicensePopup.value = true;
}

async function handleCustomerSelected(customer: any) {
  console.log("Customer selected from popup:", customer);
  if (!customer) return;

  isManuallySelectingCustomer.value = true;
  isUpdatingInternally.value = true;

  try {
    safeSetField("customer_name", customer.name || customer.customer_name || "");
    safeSetField("customer_code", customer.custom_customercode || "");
    lastValidatedCustomerCode.value = customer.custom_customercode || "";
    await nextTick();
  } finally {
    isUpdatingInternally.value = false;
    isManuallySelectingCustomer.value = false;
  }
}

async function saveAlert() {
  if (!newAlert.customer_name || !newAlert.customer_code || !newAlert.popupmessage) {
    $dialog({ title: "Missing Information", message: "Please fill all required fields" });
    return;
  }
  
  isSaving.value = true;
  try {
    await call("frappe.client.insert", {
      doc: { 
        doctype: "Customer Alert", 
        customer_code: newAlert.customer_code,
        customer_name: newAlert.customer_name, 
        popupmessage: newAlert.popupmessage 
      },
    });
    
    $dialog({ title: "Success", message: "Customer alert saved successfully!" });
    router.push({ name: "CustomerAlertList" });
  } catch (err) {
    console.error("Error saving customer alert:", err);
    $dialog({ title: "Error", message: "Customer Alert already exists for this Customer" });
  } finally {
    isSaving.value = false;
  }
}
</script>
