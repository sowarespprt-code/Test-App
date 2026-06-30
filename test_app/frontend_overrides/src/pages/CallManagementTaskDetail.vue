<template>
  <div v-if="task" class="flex flex-col h-full bg-gray-50">
    <!-- Header -->
    <div class="border-b px-6 py-4 flex items-center justify-between bg-white shadow-sm">
      <div class="flex items-center gap-4">
        <button
          @click="router.push({ name: 'CallManagementTaskList' })"
          class="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          title="Back to List"
        >
          <LucideArrowLeft class="w-5 h-5 text-gray-600" />
        </button>
        <div>
          <div class="flex items-center gap-3">
            <h1 class="text-2xl font-bold text-gray-900">{{ task.name }}</h1>
            <Badge :variant="'subtle'" :theme="getStatusTheme(task.status)" :label="task.status" />
            <Badge :variant="'outline'" :theme="getPriorityTheme(task.priority)" :label="task.priority + ' Priority'" />
          </div>
          <p class="text-sm text-gray-500 mt-1">Customer: <span class="font-semibold text-gray-700">{{ customerName }}</span></p>
        </div>
      </div>

      <div class="flex items-center gap-3">
        
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="flex-1 overflow-hidden flex flex-col md:flex-row">
      <!-- Left side: Activity Logs / Tables -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6">
        <!-- Stat Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex flex-col justify-between">
            <span class="text-sm font-medium text-gray-500">Total Receivable</span>
            <span class="text-2xl font-bold text-gray-900 mt-2">{{ formatCurrency(task.payment_amount) }}</span>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex flex-col justify-between">
            <span class="text-sm font-medium text-gray-500">Total Collected</span>
            <span class="text-2xl font-bold text-green-600 mt-2">{{ formatCurrency(task.collected_amount) }}</span>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex flex-col justify-between" :class="task.outstanding_amount > 0 ? 'bg-red-50/20 border-red-100' : ''">
            <span class="text-sm font-medium text-gray-500">Outstanding Balance</span>
            <span class="text-2xl font-extrabold mt-2" :class="task.outstanding_amount > 0 ? 'text-red-600' : 'text-green-600'">
              {{ formatCurrency(task.outstanding_amount) }}
            </span>
          </div>
        </div>

        <!-- Tabs Container -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div class="border-b bg-gray-50 px-6 py-4 font-semibold text-gray-900">
            Call History ({{ standaloneLogs.length || 0 }})
          </div>
          <!-- Tab Contents -->
          <div class="p-6">
            <!-- TAB 1: CALL HISTORY -->
            <div class="space-y-4">
              <div class="flex items-center justify-between mb-2">
                <h3 class="font-bold text-gray-800">Call Logs</h3>
                <Button variant="subtle" @click="openLogCallModal">
                  <template #prefix><LucidePlus class="h-4 w-4" /></template>
                  Log New Call
                </Button>
              </div>

              <div v-if="standaloneLogs && standaloneLogs.length" class="space-y-4">
                <div
                  v-for="(call, idx) in sortedCalls"
                  :key="idx"
                  class="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition bg-white"
                >
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-semibold text-gray-500 flex items-center gap-1">
                      <LucideCalendar class="w-3.5 h-3.5" />
                      {{ formatDatetime(call.call_date_and_time) }}
                    </span>
                    <span class="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
                      Logged by {{ getUserFullName(call.staff_member) }}
                    </span>
                  </div>

                  <div class="text-sm text-gray-800 font-medium">
                    Response: <span class="text-gray-600 font-normal">{{ call.customer_response }}</span>
                  </div>

                  <div v-if="call.call_outcome" class="text-sm text-gray-800 font-medium mt-1">
                    Outcome: <span class="text-gray-600 font-normal">{{ call.call_outcome }}</span>
                  </div>

                  <p class="text-sm text-gray-600 mt-2 bg-gray-50 p-2.5 rounded border border-gray-100 italic">
                    "{{ call.discussion_summary }}"
                  </p>

                  <!-- Promised Details inside call -->
                  <div v-if="call.promised_amount || call.next_follow_up_date" class="mt-3 pt-2.5 border-t border-gray-100 flex flex-wrap gap-4 text-xs">
                    <span v-if="call.promised_amount" class="text-green-700 bg-green-50 px-2 py-1 rounded font-medium">
                      Promised: {{ formatCurrency(call.promised_amount) }} on {{ formatDate(call.promised_payment_date) }}
                    </span>
                    <span v-if="call.next_follow_up_date" class="text-orange-700 bg-orange-50 px-2 py-1 rounded font-medium">
                      Next Follow-up: {{ formatDate(call.next_follow_up_date) }}
                    </span>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-10 text-gray-500 border border-dashed rounded-lg">
                No calls logged yet. Click "Log Call" to add customer feedback.
              </div>
            </div>

                      </div>
        </div>
      </div>

      <!-- Right side: Sidebar Info -->
      <div class="w-full md:w-80 border-t md:border-t-0 md:border-l border-gray-200 bg-white p-6 space-y-6 overflow-y-auto">
        <!-- Task Details -->
        <div class="space-y-4">
          <h4 class="text-xs font-bold uppercase tracking-wider text-gray-400">Assignment Details</h4>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-500">Purpose:</span>
              <span class="font-medium text-gray-900">{{ task.purpose_type }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Assignee:</span>
              <span class="font-medium text-gray-900">{{ getUserFullName(task.assigned_to) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Created:</span>
              <span class="font-medium text-gray-900">{{ formatDate(task.creation) }}</span>
            </div>
            <div class="flex justify-between" v-if="task.next_follow_up_date">
              <span class="text-gray-500">Next Follow-up:</span>
              <span class="font-bold text-orange-600 bg-orange-50 px-2 py-0.5 rounded">{{ formatDate(task.next_follow_up_date) }}</span>
            </div>
          </div>
        </div>

        <!-- Contact Info -->
        <div class="space-y-4 border-t pt-4">
          <div class="flex items-center justify-between">
            <h4 class="text-xs font-bold uppercase tracking-wider text-gray-400">Customer Contact Details</h4>
            <Button variant="solid" @click="openLogCallModal" class="bg-blue-600 hover:bg-blue-700 text-white !py-1 !px-3 text-xs">
              <template #prefix><LucidePhoneCall class="w-3.5 h-3.5" /></template>
              Call Now
            </Button>
          </div>
          <div class="space-y-3 text-sm">
            <div>
              <span class="text-gray-500 block text-xs">Primary Contact:</span>
              <span class="font-semibold text-gray-900">{{ task.contact_person }}</span>
            </div>

            <div>
              <span class="text-gray-500 block text-xs">Primary Mobile:</span>
              <a :href="'tel:' + task.mobile_number" class="inline-flex items-center gap-1 font-bold text-blue-600 hover:underline">
                <LucidePhone class="w-3.5 h-3.5 text-blue-500" />
                {{ task.mobile_number }}
              </a>
            </div>

            <div v-if="task.alternate_mobile">
              <span class="text-gray-500 block text-xs">Alternate Mobile:</span>
              <a :href="'tel:' + task.alternate_mobile" class="inline-flex items-center gap-1 font-medium text-gray-700 hover:underline">
                <LucidePhone class="w-3.5 h-3.5 text-gray-400" />
                {{ task.alternate_mobile }}
              </a>
            </div>
          </div>
        </div>

        <!-- Description -->
        <div class="space-y-4 border-t pt-4">
          <h4 class="text-xs font-bold uppercase tracking-wider text-gray-400">Purpose Description</h4>
          <p class="text-sm text-gray-600 whitespace-pre-wrap leading-relaxed bg-gray-50 p-3 rounded-lg border border-gray-100">
            {{ task.task_description }}
          </p>
        </div>
      </div>
    </div>

    <!-- DIALOG MODAL: LOG CALL -->
    <Dialog
      v-model="callModalOpen"
      :options="{
        title: 'Log Customer Follow-up Call',
        size: 'xl'
      }"
    >
      <template #body-content>
        <div class="space-y-4 p-1">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Customer Response -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Customer Response <span class="text-red-500">*</span></label>
              <input
                v-model="callForm.customer_response"
                type="text"
                placeholder="e.g. Promised payment / Asked to call back"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                required
              />
            </div>

            <!-- Call Outcome -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Call Outcome</label>
              <input
                v-model="callForm.call_outcome"
                type="text"
                placeholder="e.g. Commitment recorded / Postponed / Not connected"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <!-- Next Follow-up Date -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Next Follow-up Date</label>
              <input
                v-model="callForm.next_follow_up_date"
                type="date"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              />
            </div>
          </div>

          <div class="border-t border-gray-100 my-4 pt-3">
            <h5 class="text-sm font-bold text-gray-800 mb-3">Record Payment Promise (Optional)</h5>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 bg-green-50/30 border border-green-100 p-4 rounded-lg">
              <!-- Promised Amount -->
              <div>
                <label class="block text-xs font-semibold text-green-800 mb-1">Promised Amount (INR)</label>
                <input
                  v-model="callForm.promised_amount"
                  type="number"
                  placeholder="0"
                  class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-green-500 focus:outline-none bg-white font-semibold"
                />
              </div>

              <!-- Promised Payment Date -->
              <div>
                <label class="block text-xs font-semibold text-green-800 mb-1">Expected Payment Date</label>
                <input
                  v-model="callForm.promised_payment_date"
                  type="date"
                  class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-green-500 focus:outline-none bg-white"
                />
              </div>
            </div>
          </div>

          <!-- Discussion Summary -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1">Discussion Summary <span class="text-red-500">*</span></label>
            <textarea
              v-model="callForm.discussion_summary"
              rows="3"
              placeholder="Write detailed call summary of the conversation with customer..."
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              required
            ></textarea>
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end gap-2 mt-4">
          <Button variant="subtle" @click="callModalOpen = false">Close</Button>
          <Button variant="solid" :loading="isCallSaving" @click="saveCallLog" class="bg-blue-600 text-white hover:bg-blue-700">Save Call</Button>
        </div>
      </template>
    </Dialog>

    
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { call, Button, Badge, Dialog } from "frappe-ui";
import LucideArrowLeft from "~icons/lucide/arrow-left";
import LucidePhoneCall from "~icons/lucide/phone-call";
import LucidePlus from "~icons/lucide/plus";
import LucidePhone from "~icons/lucide/phone";
import LucideCalendar from "~icons/lucide/calendar";

const props = defineProps({
  taskId: {
    type: String,
    required: true
  }
});

const router = useRouter();
const task = ref<any>(null);
const customerName = ref("");
const standaloneLogs = ref<any[]>([]);

// Cache maps
const userMap = ref<Record<string, string>>({});

// Modals
const callModalOpen = ref(false);
const isCallSaving = ref(false);
const callForm = ref({
  discussion_summary: "",
  customer_response: "",
  call_outcome: "",
  promised_amount: null as number | null,
  promised_payment_date: "",
  next_follow_up_date: ""
});

const receiptModalOpen = ref(false);
const isReceiptSaving = ref(false);
const receiptForm = ref({
  amount_received: 0,
  payment_mode: "Bank Transfer",
  transaction_reference: "",
  remarks: ""
});

onMounted(async () => {
  await fetchTaskDetails();
  await fetchUsers();
});

async function fetchTaskDetails() {
  try {
    const doc = await call("frappe.client.get", {
      doctype: "Payment Collection Task",
      name: props.taskId
    });
    task.value = doc;

    // Fetch customer display name
    if (doc.customer) {
      const cust = await call("frappe.client.get_value", {
        doctype: "HD Customer",
        filters: { name: doc.customer },
        fieldname: "customer_name"
      });
      customerName.value = cust?.customer_name || doc.customer;
    }

    const logs = await call("test_app.api.get_call_management_logs", {
      task_id: props.taskId
    });
    standaloneLogs.value = logs || [];
  } catch (err) {
    console.error("Failed to load task details:", err);
    alert("Failed to load payment collection task details.");
  }
}

async function fetchUsers() {
  try {
    const list = await call("frappe.client.get_list", {
      doctype: "User",
      fields: ["name", "full_name"],
      limit_page_length: 500
    });
    list.forEach((u: any) => {
      userMap.value[u.name] = u.full_name || u.name;
    });
  } catch (err) {
    console.error("Failed to load users list:", err);
  }
}

const sortedCalls = computed(() => {
  if (!standaloneLogs.value) return [];
  return [...standaloneLogs.value];
});

function getUserFullName(email: string) {
  return userMap.value[email] || email;
}

// Log Call Modal actions
function openLogCallModal() {
  callForm.value = {
    discussion_summary: "",
    customer_response: "",
    call_outcome: "",
    promised_amount: null,
    promised_payment_date: "",
    next_follow_up_date: ""
  };
  callModalOpen.value = true;
}

async function saveCallLog() {
  if (!callForm.value.customer_response || !callForm.value.discussion_summary) {
    alert("Please fill in the customer response and discussion summary.");
    return;
  }
  isCallSaving.value = true;
  try {
    await call("test_app.api.log_management_call", {
      task_id: props.taskId,
      ...callForm.value
    });
    callModalOpen.value = false;
    await fetchTaskDetails(); // Full sync
  } catch (err: any) {
    console.error("Failed to log call:", err);
    alert(err.message || "Failed to log call.");
  } finally {
    isCallSaving.value = false;
  }
}

// UI Formatting helpers
function formatCurrency(val: any) {
  const num = parseFloat(val) || 0.0;
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0
  }).format(num);
}

function formatDate(dateStr: string) {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleDateString("en-IN", {
    year: "numeric",
    month: "short",
    day: "numeric"
  });
}

function formatDatetime(datetimeStr: string) {
  if (!datetimeStr) return "";
  return new Date(datetimeStr).toLocaleString("en-IN", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  });
}

function getStatusTheme(status: string) {
  switch (status) {
    case "Open":
      return "blue";
    case "In Progress":
      return "orange";
    case "Partially Paid":
      return "yellow";
    case "Completed":
      return "green";
    case "Cancelled":
      return "gray";
    default:
      return "blue";
  }
}

function getPriorityTheme(priority: string) {
  switch (priority) {
    case "Urgent":
      return "red";
    case "High":
      return "orange";
    case "Medium":
      return "blue";
    case "Low":
      return "gray";
    default:
      return "blue";
  }
}
</script>
