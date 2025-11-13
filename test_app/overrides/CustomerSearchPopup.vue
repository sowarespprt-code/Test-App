<template>
  <!-- Customer Search Popup -->
  <div
    v-if="modelValue"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
    @click.self="closePopup"
  >
    <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden">
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
      <div class="px-5 py-4 overflow-y-auto max-h-[calc(90vh-140px)]">
        <!-- Search Input -->
        <div class="mb-4 sticky top-0 z-10 bg-white pt-4 pb-3 border-b border-gray-300">
          <div class="relative">
            <input
              v-model="searchQuery"
              @input="handleSearch"
              type="text"
              placeholder="Search by customer name, email, or phone..."
              class="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              autofocus
            />
            <svg
              class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400"
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
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
          </div>
        </div>

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
          <div
            v-for="customer in searchResults"
            :key="customer.name"
            class="p-3 md:p-4 border rounded-lg cursor-pointer transition-all"
            :class="selectedCustomer?.name === customer.name 
              ? 'bg-blue-50 border-blue-400' 
              : 'border-gray-200 hover:bg-gray-50 hover:border-gray-300'"
            @click="handleSelectCustomer(customer)"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="flex-1 min-w-0">
                <h3 class="font-semibold text-gray-900 mb-2 text-sm md:text-base break-words">
                  {{ customer.customer_name }}
                </h3>
                
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs md:text-sm">
                  <div v-if="customer.custom_customercode" class="break-words">
                    <span class="text-gray-500">Customer Code:</span>
                    <span class="ml-1 text-gray-900 font-medium">{{ customer.custom_customercode }}</span>
                  </div>
                  
                  <div v-if="customer.custom_productname" class="break-words">
                    <span class="text-gray-500">Product:</span>
                    <span class="ml-1 text-gray-900">{{ customer.custom_productname }}</span>
                  </div>
                  
                  <div v-if="customer.custom_address1" class="break-words">
                    <span class="text-gray-500">Address1:</span>
                    <span class="ml-1 text-gray-900 font-medium">{{ customer.custom_address1 }}</span>
                  </div>
                  
                  <div v-if="customer.custom_address2" class="break-words">
                    <span class="text-gray-500">Address2:</span>
                    <span class="ml-1 text-gray-900 font-medium">{{ customer.custom_address2 }}</span>
                  </div>
                  
                  <div v-if="customer.custom_place" class="break-words">
                    <span class="text-gray-500">Place:</span>
                    <span class="ml-1 text-gray-900 font-medium">{{ customer.custom_place }}</span>
                  </div>
                  
                  <div v-if="customer.custom_district" class="break-words">
                    <span class="text-gray-500">District:</span>
                    <span class="ml-1 text-gray-900">{{ customer.custom_district }}</span>
                  </div>
                  
                  <div v-if="customer.custom_phone001" class="col-span-1 sm:col-span-2 break-words">
                    <span class="text-gray-500">Phone1:</span>
                    <span class="ml-1 text-gray-900">{{ customer.custom_phone001 }}</span>
                  </div>
                  
                  <div v-if="customer.custom_phone002" class="col-span-1 sm:col-span-2 break-words">
                    <span class="text-gray-500">Phone2:</span>
                    <span class="ml-1 text-gray-900">{{ customer.custom_phone002 }}</span>
                  </div>
                </div>
              </div>
              
              <svg
                class="h-5 w-5 flex-shrink-0 mt-1"
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

      <!-- Popup Footer -->
      <div class="flex items-center justify-between px-5 py-3 border-t bg-gray-50">
        <div v-if="selectedCustomer" class="text-sm text-gray-600">
          Selected: <span class="font-semibold text-gray-900">{{ selectedCustomer.customer_name }}</span>
        </div>
        <div v-else class="text-sm text-gray-500">
          Select a customer to continue
        </div>
        <div class="flex items-center gap-2">
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
import { ref, watch } from "vue";
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
  custom_email?: string;
  custom_productname?: string;
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
let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null;

function closePopup() {
  emit("update:modelValue", false);
    if (!showDetailsPopup.value) {
    searchQuery.value = "";
    searchResults.value = [];
    selectedCustomer.value = null;
  }
}

function handleSearch() {
  // Clear previous timer
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer);
  }
 
  const query = searchQuery.value.trim();
 
  // Reset selected customer when search changes
  selectedCustomer.value = null;
 
  // Only search if we have at least 1 characters
  if (query.length >= 1) {
    searchDebounceTimer = setTimeout(() => {
      searchCustomers(query);
    }, 1000); // 1000ms debounce as per requirement
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
    // Call your custom API
    const results = await call("helpdesk.api.customer_api.search_hd_customers", {
      search_term: query
    });
   
    searchResults.value = results || [];
  } catch (error) {
    console.error("Error searching customers:", error);
    // Show error message
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