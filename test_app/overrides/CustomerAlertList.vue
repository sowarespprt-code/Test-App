<template>
  <div class="flex flex-col h-full">
    <!-- Header -->
    <div class="border-b px-5 py-4 flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">Customer Alert</h1>
      <Button variant="solid" @click="createNewAlert">
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
        
        <!-- Customer Search Button -->
        <button
          class="inline-flex items-center gap-2 px-4 py-2 text-sm bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg transition-colors duration-200 shadow-sm whitespace-nowrap"
          type="button"
          @click.stop.prevent="openSearchCustomerPopupForFilter"
          title="Search Customer"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          <span>Search Customer</span>
        </button>
        
        <Button v-if="searchQuery" variant="subtle" @click="searchQuery = ''" class="text-sm">Clear</Button>
      </div>
    </div>

    <!-- Alert List -->
    <div class="flex-1 overflow-auto">
      <div v-if="filteredAlerts.length" class="border-b">
        <table class="w-full divide-y">
          <thead class="bg-gray-50 sticky top-0">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Customer Code</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Customer</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Popup Message</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Created On</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="alert in filteredAlerts" :key="alert.name" class="hover:bg-gray-50 cursor-pointer transition-colors" @click="openAlertDetail(alert)">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ alert.customer_code || 'N/A' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ alert.customer_name || 'N/A' }}</div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-700 truncate max-w-md">{{ alert.popupmessage || 'N/A' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{{ formatDate(alert.creation) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else-if="!alerts.length" class="flex h-full flex-col items-center justify-center gap-4">
        <div class="text-base text-gray-600">No customer alerts found</div>
        <Button @click="createNewAlert">
          <template #prefix><LucidePlus class="h-4 w-4" /></template>
          Create your first alert
        </Button>
      </div>

      <div v-else class="flex h-full flex-col items-center justify-center gap-4">
        <div class="text-base text-gray-600">No alerts found for "{{ searchQuery }}"</div>
        <Button variant="subtle" @click="searchQuery = ''">Clear search</Button>
      </div>
    </div>

    <!-- CustomerSearchPopup for LIST FILTER -->
    <Teleport to="body">
      <CustomerSearchPopup
        v-if="showFilterSearchPopup"
        v-model="showFilterSearchPopup"
        @customerSelected="handleFilterCustomerSelected"
      />
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { call, Button } from "frappe-ui";
import LucidePlus from "~icons/lucide/plus";
import LucideSearch from "~icons/lucide/search";
import { useRouter } from "vue-router";
import CustomerSearchPopup from "@/components/CustomerSearchPopup.vue";

const router = useRouter();

const alerts = ref<any[]>([]);
const searchQuery = ref("");
const showFilterSearchPopup = ref(false);

onMounted(async () => {
  await fetchAlerts();
});

async function fetchAlerts() {
  try {
    const data = await call("frappe.client.get_list", {
      doctype: "Customer Alert",
      fields: ["name", "customer_code", "customer_name", "popupmessage", "creation"],
      order_by: "creation desc",
      limit_page_length: 999,
    });
    alerts.value = data || [];
  } catch (err) {
    console.error("Failed to fetch alerts:", err);
  }
}

function openSearchCustomerPopupForFilter() {
  showFilterSearchPopup.value = true;
}

async function handleFilterCustomerSelected(customer: any) {
  console.log("Filter customer selected:", customer);
  if (!customer) return;
  searchQuery.value = customer.customer_name || customer.name || "";
  showFilterSearchPopup.value = false;
}

function createNewAlert() {
  router.push({ name: "CustomerAlertNew" });
}

function openAlertDetail(alert: any) {
  router.push({ name: "CustomerAlertDetail", params: { alertId: alert.name } });
}

function formatDate(date: string) {
  if (!date) return "";
  return new Date(date).toLocaleDateString();
}

const filteredAlerts = computed(() => {
  if (!searchQuery.value) return alerts.value;
  const query = searchQuery.value.toLowerCase();
  return alerts.value.filter((item: any) => 
    item.customer_name?.toLowerCase().includes(query) || 
    item.customer_code?.toLowerCase().includes(query)
  );
});
</script>
