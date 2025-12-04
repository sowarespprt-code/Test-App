<template>
  <div class="flex flex-col h-full">
    <!-- ========== LIST VIEW ========== -->
    <template v-if="!showNewAlertForm">
      <!-- Header -->
      <div class="border-b px-5 py-4 flex items-center justify-between">
        <h1 class="text-2xl font-semibold text-gray-900">Customer Alert</h1>
        <Button variant="solid" @click="openNewAlertForm">
          <template #prefix>
            <LucidePlus class="h-4 w-4" />
          </template>
          New
        </Button>
      </div>

      <!-- Search and Filter Bar -->
      <div class="border-b px-5 py-3 bg-gray-50">
        <div class="flex items-center gap-3">
          <div class="relative flex-1 max-w-md">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Customer Name"
              class="w-full px-3 py-2 pr-8 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <LucideSearch class="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          </div>
          <Button v-if="searchQuery" variant="subtle" @click="searchQuery = ''" class="text-sm">Clear</Button>
        </div>
      </div>

      <!-- Alert List -->
      <div class="flex-1 overflow-auto">
        <div v-if="filteredAlerts.length" class="border-b">
          <table class="w-full divide-y">
            <thead class="bg-gray-50 sticky top-0">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Customer</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Remarks</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Created On</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="alert in filteredAlerts" :key="alert.name" class="hover:bg-gray-50 cursor-pointer transition-colors" @click="openAlertDetail(alert)">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">{{ alert.customer_name || 'N/A' }}</div>
                </td>
                <td class="px-6 py-4">
                  <div class="text-sm text-gray-700 truncate max-w-md">{{ alert.remarks || 'N/A' }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{{ formatDate(alert.creation) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else-if="!alerts.length" class="flex h-full flex-col items-center justify-center gap-4">
          <div class="text-base text-gray-600">No customer alerts found</div>
          <Button @click="openNewAlertForm">
            <template #prefix><LucidePlus class="h-4 w-4" /></template>
            Create your first alert
          </Button>
        </div>

        <div v-else class="flex h-full flex-col items-center justify-center gap-4">
          <div class="text-base text-gray-600">No alerts found for "{{ searchQuery }}"</div>
          <Button variant="subtle" @click="searchQuery = ''">Clear search</Button>
        </div>
      </div>
    </template>

    <!-- ========== FULL SIZE NEW ALERT FORM ========== -->
    <template v-else>
      <!-- Header with Back Button -->
      <div class="border-b px-5 py-4 flex items-center justify-between bg-white">
        <div class="flex items-center gap-4">
          <button
            @click="cancelNewAlertForm"
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
          <Button variant="subtle" @click="cancelNewAlertForm">Cancel</Button>
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

      <!-- Full Size Form Content -->
      <div class="flex-1 overflow-y-auto bg-gray-50">
        <div class="max-w-4xl mx-auto p-8">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
            <div class="space-y-8">
              <!-- Customer Selection Row -->
              <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Customer Code Field -->
                <div class="w-full">
                  <label class="block text-sm font-semibold text-gray-700 mb-2">
                    Customer Code <span class="text-red-500">*</span>
                  </label>
                  <div class="flex gap-3 items-end">
                    <div class="flex-1 min-w-0">
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
                    <!-- Customer Search Button -->
                    <button
                      class="inline-flex items-center gap-2 px-4 py-3 text-sm bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg transition-colors duration-200 shadow-sm whitespace-nowrap flex-shrink-0"
                      type="button"
                      @click.stop.prevent="openCustomerSearchPopup"
                      title="Search Customer Details"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="11" cy="11" r="8"></circle>
                        <path d="m21 21-4.35-4.35"></path>
                      </svg>
                      <span>Search</span>
                    </button>
                  </div>
                </div>

                <!-- Customer Name Field -->
                <div class="w-full">
                  <label class="block text-sm font-semibold text-gray-700 mb-2">
                    Customer Name <span class="text-red-500">*</span>
                  </label>
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
              </div>

              <!-- Remarks Field - Full Width Large Textarea -->
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">
                  Remarks <span class="text-red-500">*</span>
                </label>
                <textarea
                  v-model="newAlert.remarks"
                  rows="12"
                  class="w-full rounded-lg border border-gray-300 px-4 py-4 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-vertical"
                  placeholder="Enter detailed remarks for this customer alert..."
                ></textarea>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- CustomerSearchPopup - Teleported to body -->
    <Teleport to="body">
      <CustomerSearchPopup
        v-if="showCustomerSearchPopup"
        v-model="showCustomerSearchPopup"
        @customerSelected="handleCustomerSelected"
      />
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive, nextTick } from "vue";
import { call } from "frappe-ui";
import { Button, Autocomplete } from "frappe-ui";
import LucidePlus from "~icons/lucide/plus";
import LucideSearch from "~icons/lucide/search";
import { useRouter } from "vue-router";
import { globalStore } from "@/stores/globalStore";
import CustomerSearchPopup from "@/components/CustomerSearchPopup.vue";

const router = useRouter();
const { $dialog } = globalStore();

const alerts = ref<any[]>([]);
const searchQuery = ref("");
const customerOptions = ref<any[]>([]);
const invalidCodeError = ref("");
const showNewAlertForm = ref(false); // Toggle between list and form view
const isSaving = ref(false);
const newAlert = reactive({ customer_name: "", customer_code: "", remarks: "" });

// Customer Code State
const isFetchingCustomerName = ref(false);
const lastValidatedCustomerCode = ref("");
const MIN_CODE_LENGTH = 3;
const isUpdatingInternally = ref(false);
const isManuallySelectingCustomer = ref(false);
const showCustomerSearchPopup = ref(false);

onMounted(async () => {
  await fetchAlerts();
});

async function fetchAlerts() {
  try {
    const data = await call("frappe.client.get_list", {
      doctype: "Customer Alert",
      fields: ["name", "customer_name", "remarks", "creation"],
      order_by: "creation desc",
      limit_page_length: 999,
    });
    alerts.value = data || [];
  } catch (err) {
    console.error("Failed to fetch alerts:", err);
  }
}

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

// EXACT TicketNew.vue helper functions
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
  invalidCodeError.value = "";

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

  if (enteredCode === previousCode) return;

  safeSetField("customer_code", enteredCode);
  const found = await fetchCustomerName(enteredCode);
  if (found) {
    lastValidatedCustomerCode.value = enteredCode;
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

// ===== Customer Popup Functions =====
function openCustomerSearchPopup() {
  showCustomerSearchPopup.value = true;
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

// ===== Form View Functions =====
function openNewAlertForm() {
  newAlert.customer_name = "";
  newAlert.customer_code = "";
  newAlert.remarks = "";
  customerOptions.value = [];
  lastValidatedCustomerCode.value = "";
  showCustomerSearchPopup.value = false;
  searchCustomers("");
  showNewAlertForm.value = true;
}

function cancelNewAlertForm() {
  showNewAlertForm.value = false;
  showCustomerSearchPopup.value = false;
  newAlert.customer_name = "";
  newAlert.customer_code = "";
  newAlert.remarks = "";
}

async function saveAlert() {
  if (!newAlert.customer_name || !newAlert.customer_code || !newAlert.remarks) {
    $dialog({ title: "Missing Information", message: "Please fill all required fields" });
    return;
  }
  isSaving.value = true;
  try {
    await call("frappe.client.insert", {
      doc: { doctype: "Customer Alert", customer_name: newAlert.customer_name, remarks: newAlert.remarks },
    });
    showNewAlertForm.value = false;
    await fetchAlerts();
    $dialog({ title: "Success", message: "Customer alert saved successfully!" });
  } catch (err) {
    console.error("Error saving customer alert:", err);
    $dialog({ title: "Error", message: "Customer Alert already exists for this Customer" });
  } finally {
    isSaving.value = false;
  }
}

const openAlertDetail = (alert: any) => {
  router.push({ name: "CustomerAlertDetail", params: { alertId: alert.name } });
};

const formatDate = (date: string) => {
  if (!date) return "";
  return new Date(date).toLocaleDateString();
};

const filteredAlerts = computed(() => {
  if (!searchQuery.value) return alerts.value;
  const query = searchQuery.value.toLowerCase();
  return alerts.value.filter((item: any) => item.customer_name?.toLowerCase().includes(query));
});
</script>
