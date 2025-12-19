<template>
  <!-- Customer Search Popup -->
  <div
    v-if="modelValue"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
    @click.self="closePopup"
  >
    <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-hidden">
      <!-- Popup Header -->
      <div class="flex items-center justify-between px-5 py-3 border-b bg-gray-50">
        <h2 class="text-lg font-semibold text-gray-800">Search Customer Details</h2>
        <button
          @click="closePopup"
          class="text-gray-500 hover:text-gray-700 transition"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <!-- Popup Body -->
      <div class="overflow-y-auto max-h-[calc(90vh-140px)]">
        <!-- Search Input - Fixed at top -->
        <div class="sticky top-0 z-20 bg-white px-5 pt-4 pb-3 border-b border-gray-100">
          <div class="relative">
            <input
              ref="searchInputRef"
              v-model="searchQuery"
              @input="handleSearch"
              type="text"
              placeholder="Search by customer name, code, address, phone..."
              class="w-full px-4 py-2.5 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              autofocus
              tabindex="0"
            />
            <svg
              class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400"
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
          </div>
        </div>
       
        <!-- Results Container -->
        <div class="px-5 py-4">

        <!-- Loading State -->
        <div v-if="isSearching" class="flex items-center justify-center py-8">
          <div class="flex flex-col items-center gap-2">
            <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
            <p class="text-sm text-gray-600">Searching customers...</p>
          </div>
        </div>

        <!-- No Results -->
        <div v-else-if="searchQuery && searchResults.length === 0 && !isSearching" class="py-8 text-center">
          <svg
            class="mx-auto h-12 w-12 text-gray-400 mb-3"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p class="text-gray-600">No customers found</p>
          <p class="text-sm text-gray-500 mt-1">Try a different search term</p>
        </div>

        <!-- Search Results -->
        <div v-else-if="searchResults.length > 0" class="space-y-2">
          <div class="text-xs text-gray-500 mb-2 px-1">
            Found {{ searchResults.length }} customer(s)
          </div>
          <div
            v-for="customer in searchResults"
            :key="customer.name"
            class="p-2.5 border rounded-md cursor-pointer transition-all"
            :class="selectedCustomer?.name === customer.name
              ? 'bg-blue-50 border-blue-400 shadow-sm'
              : 'border-gray-200 hover:bg-gray-50 hover:border-gray-300 hover:shadow-sm'"
            @click="handleSelectCustomer(customer)"
          >
            <!-- Line 1: Customer Name, Code and Icon -->
            <div class="flex items-center justify-between gap-2 mb-1">
              <div class="flex items-center gap-2 flex-1 min-w-0">
                <h3 class="font-semibold text-gray-900 text-sm leading-tight truncate">
                  {{ customer.customer_name }}
                </h3>
                <span v-if="customer.custom_customercode" class="text-xs text-gray-600 flex-shrink-0">
                  ({{ customer.custom_customercode }})
                </span>
              </div>
              <svg
                class="h-4 w-4 flex-shrink-0"
                :class="selectedCustomer?.name === customer.name ? 'text-blue-500' : 'text-gray-400'"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fill-rule="evenodd"
                  d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                  clip-rule="evenodd"
                />
              </svg>
            </div>
           
            <!-- Line 2: Product and Address Details -->
            <div class="text-xs text-gray-600 leading-relaxed">
              <span v-if="customer.custom_productname" class="font-medium">Product: </span><span v-if="customer.custom_productname">{{ customer.custom_productname }}</span><span v-if="customer.custom_productname && (customer.custom_address1 || customer.custom_address2 || customer.custom_place || customer.custom_district)"> | </span><span v-if="customer.custom_address1 || customer.custom_address2 || customer.custom_place || customer.custom_district" class="font-medium">Address: </span><template v-if="customer.custom_address1 || customer.custom_address2 || customer.custom_place || customer.custom_district"><span v-if="customer.custom_address1">{{ customer.custom_address1 }}</span><span v-if="customer.custom_address1 && (customer.custom_address2 || customer.custom_place || customer.custom_district)">, </span><span v-if="customer.custom_address2">{{ customer.custom_address2 }}</span><span v-if="customer.custom_address2 && (customer.custom_place || customer.custom_district)">, </span><span v-if="customer.custom_place">{{ customer.custom_place }}</span><span v-if="customer.custom_place && customer.custom_district">, </span><span v-if="customer.custom_district">{{ customer.custom_district }}</span></template><span v-if="(customer.custom_productname || customer.custom_address1 || customer.custom_address2 || customer.custom_place || customer.custom_district) && (customer.custom_phone001 || customer.custom_phone002)"> | </span><span v-if="customer.custom_phone001 || customer.custom_phone002" class="font-medium">Phone: </span><span v-if="customer.custom_phone001">{{ customer.custom_phone001 }}</span><span v-if="customer.custom_phone001 && customer.custom_phone002">, </span><span v-if="customer.custom_phone002">{{ customer.custom_phone002 }}</span>
            </div>
          </div>
        </div>

        <!-- Initial State -->
        <div v-else class="py-8 text-center">
          <svg
            class="mx-auto h-12 w-12 text-gray-400 mb-3"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <p class="text-gray-600">Start typing to search for customers</p>
          <p class="text-sm text-gray-500 mt-1">Enter at least 2 characters</p>
        </div>
        </div>
      </div>

      <!-- Popup Footer -->
      <div class="flex items-center justify-between px-5 py-3 border-t bg-gray-50">
        <div v-if="selectedCustomer" class="text-sm text-gray-600 flex-1 mr-4 truncate">
          Selected: <span class="font-semibold text-gray-900">{{ selectedCustomer.customer_name }}</span>
        </div>
        <div v-else class="text-sm text-gray-500 flex-1 mr-4">
          Select a customer to continue
        </div>
        <div class="flex items-center gap-2 flex-shrink-0">
          <Button
            label="Close"
            theme="gray"
            variant="subtle"
            @click="closePopup"
          />
          <Button
            label="OK"
            theme="blue"
            variant="solid"
            :disabled="!selectedCustomer || isFetchingDetails"
            :loading="isFetchingDetails"
            @click="handleDetailsOK"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted } from "vue";
import { Button, call } from "frappe-ui";

interface Customer {
  name: string;
  customer_name: string;
  custom_sl_no?: string;
  custom_customercode?: string;
  custom_address1?: string;
  custom_address2?: string;
  custom_place?: string;
  custom_district?: string;
  custom_state?: string;
  custom_country?: string;
  custom_contactperson?: string;
  custom_phone001?: string;
  custom_phone002?: string;
  custom_gstno?: string;
  custom_email?: string;
  custom_productname?: string;
  custom_nooflicense?: string;
  custom_dateofamclastpaid?: string;
}

interface CustomerSearchResult {
  name: string;
  customer_name: string;
  custom_sl_no?: string;
  custom_customercode?: string;
  custom_place?: string;
  custom_phone001?: string;
  custom_phone002?: string;
  custom_email?: string;
  custom_productname?: string;
  custom_address1?: string;
  custom_address2?: string;
  custom_district?: string;
}

interface Props {
  modelValue: boolean;
}

interface Emits {
  (e: "update:modelValue", value: boolean): void;
  (e: "customerSelected", customer: Customer): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();
const showDetailsPopup = ref(false);

const searchQuery = ref("");
const searchResults = ref<CustomerSearchResult[]>([]);
const selectedCustomer = ref<CustomerSearchResult | null>(null);
const isSearching = ref(false);
const isFetchingDetails = ref(false);
const searchInputRef = ref<HTMLInputElement | null>(null);
let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null;

onMounted(() => {
  // Force focus when component mounts
  if (props.modelValue) {
    setTimeout(() => {
      searchInputRef.value?.focus();
    }, 150);
  }
});

// Watch for when popup opens and focus the input
watch(() => props.modelValue, async (newValue) => {
  if (newValue) {
    // Multiple attempts to ensure focus works in all contexts
    await nextTick();
    
    // First attempt
    searchInputRef.value?.focus();
    
    // Second attempt after animation delay
    setTimeout(() => {
      searchInputRef.value?.focus();
    }, 100);
    
    // Third attempt for stubborn cases (nested modals, stacking contexts)
    setTimeout(() => {
      searchInputRef.value?.focus();
    }, 300);
  } else {
    // Clear search when closing
    searchQuery.value = "";
    searchResults.value = [];
    selectedCustomer.value = null;
  }
});

function closePopup() {
  emit("update:modelValue", false);
  if (!showDetailsPopup.value) {
    searchQuery.value = "";
    searchResults.value = [];
    selectedCustomer.value = null;
  }
}

function handleSearch() {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer);
  }
  
  const query = searchQuery.value.trim();
  selectedCustomer.value = null;
  
  // Search with just 1 character minimum
  if (query.length >= 1) {
    searchDebounceTimer = setTimeout(() => {
      searchCustomers(query);
    }, 1000); // Reduced from 2000ms
  } else {
    searchResults.value = [];
  }
}

async function searchCustomers(query: string) {
  if (!query || query.length < 1) {
    searchResults.value = [];
    return;
  }
 
  isSearching.value = true;
  try {
    // Call the multi-word search API
    const results = await call("helpdesk.api.customer_api.search_hd_customers", {
      search_term: query
    });
   
    searchResults.value = results || [];
  } catch (error) {
    console.error("Error searching customers:", error);
    alert('Failed to search customers. Please try again.');
    searchResults.value = [];
  } finally {
    isSearching.value = false;
  }
}

function handleSelectCustomer(customer: CustomerSearchResult) {
  selectedCustomer.value = customer;
}

async function handleDetailsOK() {
  if (!selectedCustomer.value) return;
 
  isFetchingDetails.value = true;

  try {
    // Fetch full customer details first
    const details = await call("helpdesk.api.customer_api.get_hd_customer_details", {
      customer_name: selectedCustomer.value.name,
    });
   
    if (details) {
      // Emit the customer data
      emit("customerSelected", {
        customer_name: details.customer_name,
        custom_productname: details.custom_productname,
        custom_customercode: details.custom_customercode
      });
     
      // Close popup and reset
      searchQuery.value = "";
      searchResults.value = [];
      selectedCustomer.value = null;
      emit("update:modelValue", false);
    } else {
      alert("No customer details returned");
    }
  } catch (error) {
    console.error("Error fetching customer details:", error);
    alert("Failed to fetch customer details. Please try again.");
  } finally {
    isFetchingDetails.value = false;
  }
}
</script>