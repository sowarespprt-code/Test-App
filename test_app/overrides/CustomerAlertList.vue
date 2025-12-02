<template>
  <div class="flex flex-col h-full">
    <!-- Header -->
    <div class="border-b px-5 py-4 flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">Customer Alert</h1>
      <Button variant="solid" @click="openNewAlertModal">
        <template #prefix>
          <LucidePlus class="h-4 w-4" />
        </template>
        New
      </Button>
    </div>

    <!-- Search and Filter Bar -->
    <div class="border-b px-5 py-3 bg-gray-50">
      <div class="flex items-center gap-3">
        <!-- Search Input -->
        <div class="relative flex-1 max-w-md">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Customer Name"
            class="w-full px-3 py-2 pr-8 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <LucideSearch class="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        </div>
        
        <!-- Clear button (optional) -->
        <Button 
          v-if="searchQuery" 
          variant="subtle" 
          @click="searchQuery = ''"
          class="text-sm"
        >
          Clear
        </Button>
      </div>
    </div>

    <!-- Alert List -->
    <div class="flex-1 overflow-auto">
      <div v-if="filteredAlerts.length" class="border-b">
        <table class="w-full divide-y">
          <thead class="bg-gray-50 sticky top-0">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Customer
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Remarks
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Created On
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="alert in filteredAlerts"
              :key="alert.name"
              class="hover:bg-gray-50 cursor-pointer transition-colors"
              @click="openAlertDetail(alert)"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  {{ alert.customer_name || 'N/A' }}
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-700 truncate max-w-md">
                  {{ alert.remarks || 'N/A' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                {{ formatDate(alert.creation) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Empty State -->
      <div v-else-if="!alerts.length" class="flex h-full flex-col items-center justify-center gap-4">
        <div class="text-base text-gray-600">No customer alerts found</div>
        <Button @click="openNewAlertModal">
          <template #prefix>
            <LucidePlus class="h-4 w-4" />
          </template>
          Create your first alert
        </Button>
      </div>
      
      <!-- No Search Results -->
      <div v-else class="flex h-full flex-col items-center justify-center gap-4">
        <div class="text-base text-gray-600">No alerts found for "{{ searchQuery }}"</div>
        <Button variant="subtle" @click="searchQuery = ''">
          Clear search
        </Button>
      </div>
    </div>

    <!-- New Alert Modal -->
    <Dialog
      v-model="showModal"
      :options="{ title: 'New Customer Alert', size: 'md' }"
    >
      <template #body-content>
        <div class="space-y-4">
          <!-- Customer Search -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Customer <span class="text-red-500">*</span>
            </label>
            <Autocomplete
              v-if="customerOptions.length > 0"
              v-model="newAlert.customer_name"
              :options="customerOptions"
              :placeholder="'Select customer'"
              @update:modelValue="val => newAlert.customer_name = val.value"
              @update:query="searchCustomers"
              @change="onCustomerSelect"
              required
            />
            <div v-else class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-400">
              Loading customers...
            </div>
          </div>

          <!-- Remarks -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Remarks <span class="text-red-500">*</span>
            </label>
            <textarea
              v-model="newAlert.remarks"
              rows="3"
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="Enter remarks"
              required
            />
          </div>
        </div>
      </template>

      <template #actions>
        <Button variant="subtle" @click="showModal = false">Cancel</Button>
        <Button variant="solid" :loading="isSaving" @click="saveAlert">Save</Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { call } from "frappe-ui";
import { Button, Dialog, Autocomplete } from "frappe-ui";
import LucidePlus from "~icons/lucide/plus";
import LucideSearch from "~icons/lucide/search";
import { useRouter } from "vue-router";

const router = useRouter();
const alerts = ref([]);
const searchQuery = ref("");
const customerOptions = ref([]);
const showModal = ref(false);
const isSaving = ref(false);
const newAlert = ref({ customer_name: "", remarks: "" });

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

async function searchCustomers(query) {
  try {
    const filters = query ? { customer_name: ["like", `%${query}%`] } : {};
    const data = await call("frappe.client.get_list", {
      doctype: "HD Customer",
      fields: ["name", "customer_name"],
      filters,
      limit_page_length: 20,
      order_by: "customer_name asc",
    });

    customerOptions.value = data.map(c => ({
      label: c.customer_name || c.name,
      value: c.name,
    }));
  } catch (err) {
    console.error("Failed to fetch customers:", err);
    customerOptions.value = [];
  }
}

async function onCustomerSelect(customer) {
  if (!customer) return;

  try {
    const result = await call("frappe.client.get_list", {
      doctype: "Customer Alert",
      filters: { customer_name: customer },
      fields: ["name", "customer_name", "remarks"],
      limit: 1
    });

    if (result && result.length > 0) {
      const existing = result[0];

      frappe.show_alert({
        message: `Customer Alert exists for ${customer}. Opening...`,
        indicator: "orange",
      });

      setTimeout(() => {
        frappe.set_route("Form", "Customer Alert", existing.name);
      }, 500);

    } else {
      frappe.show_alert({
        message: `No Customer Alert found for ${customer}`,
        indicator: "green",
      });
    }

  } catch (e) {
    console.error("Error checking customer alert:", e);
  }
}

// Computed filtered list
const filteredAlerts = computed(() => {
  if (!searchQuery.value) return alerts.value;
  const query = searchQuery.value.toLowerCase();
  return alerts.value.filter((item) =>
    item.customer_name?.toLowerCase().includes(query)
  );
});

function openNewAlertModal() {
  newAlert.value = { customer_name: "", remarks: "" };
  customerOptions.value = [];
  searchCustomers("");
  showModal.value = true;
}

async function saveAlert() {
  if (!newAlert.value.customer_name || !newAlert.value.remarks) {
    alert("Please fill all fields");
    return;
  }

  isSaving.value = true;
  try {
    await call("frappe.client.insert", {
      doc: {
        doctype: "Customer Alert",
        customer_name: newAlert.value.customer_name,
        remarks: newAlert.value.remarks,
      },
    });
    showModal.value = false;
    await fetchAlerts();
    alert("Customer alert saved successfully!");
  } catch (err) {
    console.error("Customer Alert already exists for this Customer :", err);
    alert("Customer Alert already exists for this Customer");
  } finally {
    isSaving.value = false;
  }
}

const openAlertDetail = (alert) => {
  router.push({ name: "CustomerAlertDetail", params: { alertId: alert.name } });
};

const formatDate = (date) => {
  if (!date) return "";
  return new Date(date).toLocaleDateString();
};
</script>