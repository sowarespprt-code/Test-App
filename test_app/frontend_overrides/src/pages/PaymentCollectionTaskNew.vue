<template>
  <div class="flex flex-col h-full bg-white">
    <!-- Header -->
    <div class="border-b px-5 py-4 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <button
          @click="router.back()"
          class="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          title="Back to List"
        >
          <LucideArrowLeft class="w-5 h-5 text-gray-600" />
        </button>
        <div>
          <h1 class="text-2xl font-semibold text-gray-900">New Payment Collection Task</h1>
          <p class="text-sm text-gray-500 mt-1">Assign a new payment collection assignment to a staff member.</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <Button variant="subtle" @click="router.back()">Cancel</Button>
        <Button variant="solid" :loading="isSaving" @click="saveTask">
          <template #prefix>
            <LucideCheck class="w-4 h-4" />
          </template>
          Create Task
        </Button>
      </div>
    </div>

    <!-- Form Content -->
    <div class="flex-1 overflow-y-auto bg-gray-50">
      <div class="max-w-4xl mx-auto p-8">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 space-y-6">
          <!-- Step 1: Customer Details -->
          <div>
            <h2 class="text-lg font-semibold text-gray-900 border-b pb-2 mb-4">1. Customer Information</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Customer Selection -->
              <div class="col-span-1 md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Customer <span class="text-red-500">*</span>
                </label>
                <div class="flex gap-3">
                  <div class="flex-1">
                    <Autocomplete
                      v-if="customerOptions && customerOptions.length > 0"
                      v-model="selectedCustomer"
                      :options="customerOptions"
                      placeholder="Search and select customer"
                      class="w-full"
                      @update:modelValue="handleCustomerChange"
                      @update:query="searchCustomers"
                    />
                    <div v-else class="w-full rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-500 bg-gray-50">
                      Loading customers...
                    </div>
                  </div>
                  <button
                    class="inline-flex items-center gap-1.5 px-4 py-2.5 text-sm bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg transition-colors duration-200 shadow-sm whitespace-nowrap flex-shrink-0"
                    type="button"
                    @click.stop.prevent="openCustomerSearchPopup"
                    title="Search Customer"
                  >
                    <LucideSearch class="w-4 h-4" />
                    <span>Search</span>
                  </button>
                </div>
              </div>

              <!-- Contact Person -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Contact Person <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="task.contact_person"
                  type="text"
                  placeholder="Primary contact name"
                  class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  required
                />
              </div>

              <!-- Mobile Number -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Mobile Number <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="task.mobile_number"
                  type="text"
                  placeholder="Primary mobile/phone"
                  class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  required
                />
              </div>

              <!-- Alternate Mobile -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Alternate Mobile
                </label>
                <input
                  v-model="task.alternate_mobile"
                  type="text"
                  placeholder="Alternate contact phone"
                  class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          <!-- Step 2: Task Specifications -->
          <div>
            <h2 class="text-lg font-semibold text-gray-900 border-b pb-2 mb-4">2. Collection Details</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Purpose Type -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Purpose Type <span class="text-red-500">*</span>
                </label>
                <select
                  v-model="task.purpose_type"
                  class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  required
                >
                  <option value="Software Payment">Software Payment</option>
                  <option value="AMC">AMC</option>
                  <option value="New Feature">New Feature</option>
                  <option value="Customization">Customization</option>
                  <option value="Support">Support</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <!-- Payment Amount -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Payment Amount (INR) <span class="text-red-500">*</span>
                </label>
                <div class="relative">
                  <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm">₹</span>
                  <input
                    v-model="task.payment_amount"
                    type="number"
                    min="0"
                    placeholder="0"
                    class="w-full rounded-lg border border-gray-300 pl-7 pr-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 font-semibold"
                    required
                  />
                </div>
              </div>

              <!-- Assignee Selection -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Assigned To (Staff Member) <span class="text-red-500">*</span>
                </label>
                <Autocomplete
                  v-if="userOptions && userOptions.length > 0"
                  v-model="selectedAssignee"
                  :options="userOptions"
                  placeholder="Select staff member"
                  class="w-full"
                />
                <div v-else class="w-full rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-500 bg-gray-50">
                  Loading staff...
                </div>
              </div>

              <!-- Priority -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Priority
                </label>
                <select
                  v-model="task.priority"
                  class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Urgent">Urgent</option>
                </select>
              </div>

              <!-- Description -->
              <div class="col-span-1 md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Task Description / Notes <span class="text-red-500">*</span>
                </label>
                <textarea
                  v-model="task.task_description"
                  rows="4"
                  placeholder="Provide details about this receivable (e.g. invoice date, AMC contract details, outstanding invoice reference)"
                  class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  required
                ></textarea>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Customer Search Popup Modal -->
    <Teleport to="body">
      <CustomerSearchPopup
        v-if="showSearchPopup"
        v-model="showSearchPopup"
        @customerSelected="handleCustomerSelectedFromPopup"
      />
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { call, Button, Autocomplete } from "frappe-ui";
import LucideArrowLeft from "~icons/lucide/arrow-left";
import LucideCheck from "~icons/lucide/check";
import LucideSearch from "~icons/lucide/search";
import CustomerSearchPopup from "@/components/CustomerSearchPopup.vue";

const router = useRouter();
const isSaving = ref(false);
const showSearchPopup = ref(false);

const task = ref({
  customer: "",
  purpose_type: "Software Payment",
  task_description: "",
  assigned_to: "",
  contact_person: "",
  mobile_number: "",
  alternate_mobile: "",
  payment_amount: 0,
  priority: "Medium",
  status: "Open"
});

// Autocomplete Options
const selectedCustomer = ref<any>('');
const selectedAssignee = ref<any>('');

const customerOptions = ref<any[]>([]);
const userOptions = ref<any[]>([]);

onMounted(async () => {
  await fetchUsers();
  await searchCustomers("");
});

async function fetchUsers() {
  try {
    const list = await call("frappe.client.get_list", {
      doctype: "User",
      filters: [["enabled", "=", 1], ["user_type", "=", "System User"]],
      fields: ["name", "full_name"],
      limit_page_length: 50
    });
    userOptions.value = list.map((u: any) => ({
      label: u.full_name || u.name,
      value: u.name
    }));
  } catch (err) {
    console.error("Failed to fetch users:", err);
  }
}

async function searchCustomers(query: string) {
  try {
    const list = await call("frappe.client.get_list", {
      doctype: "HD Customer",
      filters: query ? [["customer_name", "like", `%${query}%`]] : [],
      fields: ["name", "customer_name"],
      limit_page_length: 50
    });
    customerOptions.value = list.map((c: any) => ({
      label: c.customer_name || c.name,
      value: c.name
    }));
  } catch (err) {
    console.error("Failed to fetch customers:", err);
  }
}

async function handleCustomerChange(val: any) {
  if (!val) return;
  task.value.customer = val.value;
  await autofillCustomerDetails(val.value);
}

function openCustomerSearchPopup() {
  showSearchPopup.value = true;
}

async function handleCustomerSelectedFromPopup(customer: any) {
  if (!customer) return;
  selectedCustomer.value = {
    label: customer.customer_name,
    value: customer.name
  };
  task.value.customer = customer.name;
  await autofillCustomerDetails(customer.name);
}

async function autofillCustomerDetails(customerName: string) {
  try {
    const details = await call("test_app.api.customer_api.get_hd_customer_details", {
      customer_name: customerName
    });
    if (details) {
      task.value.contact_person = details.custom_contactperson || "";
      task.value.mobile_number = details.custom_phone001 || "";
      task.value.alternate_mobile = details.custom_phone002 || "";
    }
  } catch (err) {
    console.error("Failed to auto-fill customer details:", err);
  }
}

async function saveTask() {
  // Validate required fields
  if (!task.value.customer) {
    alert("Please select a customer.");
    return;
  }
  if (!task.value.contact_person || !task.value.mobile_number) {
    alert("Please enter Contact Person and Mobile Number.");
    return;
  }
  if (!task.value.payment_amount || task.value.payment_amount <= 0) {
    alert("Please enter a valid Payment Amount greater than 0.");
    return;
  }
  if (!selectedAssignee.value) {
    alert("Please assign this task to a staff member.");
    return;
  }
  if (!task.value.task_description.trim()) {
    alert("Please enter a task description.");
    return;
  }

  isSaving.value = true;
  task.value.assigned_to = selectedAssignee.value.value;

  try {
    const res = await call("frappe.client.insert", {
      doc: {
        doctype: "Payment Collection Task",
        ...task.value
      }
    });
    if (res && res.name) {
      router.push({ name: "PaymentCollectionTaskDetail", params: { taskId: res.name } });
    }
  } catch (err: any) {
    console.error("Failed to save task:", err);
    alert(err.message || "Failed to create Payment Collection Task.");
  } finally {
    isSaving.value = false;
  }
}
</script>

<style>
/* Fix Frappe UI Autocomplete hover highlight issue */
li[role="option"]:hover,
li[role="option"][data-headlessui-state*="active"] {
  background-color: #f3f4f6 !important;
  cursor: pointer;
}
</style>
