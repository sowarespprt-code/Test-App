<template>
  <div v-if="task" class="flex flex-col h-full bg-gray-50">
    <!-- Header -->
    <div class="border-b px-6 py-4 flex items-center justify-between bg-white shadow-sm">
      <div class="flex items-center gap-4">
        <button
          @click="router.push({ name: 'PaymentCollectionTaskList' })"
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
        <select
          v-model="task.status"
          @change="updateStatus"
          class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white font-medium"
        >
          <option value="Open">Open</option>
          <option value="In Progress">In Progress</option>
          <option value="Partially Paid">Partially Paid</option>
          <option value="Completed">Completed</option>
          <option value="Cancelled">Cancelled</option>
        </select>

        <Button variant="solid" @click="openLogCallModal" class="bg-blue-600 hover:bg-blue-700 text-white">
          <template #prefix>
            <LucidePhoneCall class="w-4 h-4" />
          </template>
          Log Call
        </Button>
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
          <!-- Tab Headers -->
          <div class="border-b bg-gray-50 flex">
            <button
              v-for="tab in ['calls', 'commitments', 'receipts']"
              :key="tab"
              @click="activeTab = tab"
              class="px-6 py-4 text-sm font-semibold border-b-2 transition-all duration-150 capitalize"
              :class="activeTab === tab
                ? 'border-blue-600 text-blue-600 bg-white'
                : 'border-transparent text-gray-500 hover:text-gray-900 hover:bg-gray-100/50'"
            >
              {{ tab === 'calls' ? 'Call History (' + (task.call_history?.length || 0) + ')' : tab === 'commitments' ? 'Payment Commitments (' + (task.payment_commitments?.length || 0) + ')' : 'Receipts & Payments (' + (task.payment_receipts?.length || 0) + ')' }}
            </button>
          </div>

          <!-- Tab Contents -->
          <div class="p-6">
            <!-- TAB 1: CALL HISTORY -->
            <div v-if="activeTab === 'calls'" class="space-y-4">
              <div class="flex items-center justify-between mb-2">
                <h3 class="font-bold text-gray-800">Call Logs</h3>
                <Button variant="subtle" @click="openLogCallModal">
                  <template #prefix><LucidePlus class="h-4 w-4" /></template>
                  Log New Call
                </Button>
              </div>

              <div v-if="task.call_history && task.call_history.length" class="space-y-4">
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

            <!-- TAB 2: COMMITMENTS -->
            <div v-if="activeTab === 'commitments'" class="space-y-4">
              <h3 class="font-bold text-gray-800 mb-2">Customer Payment Promises</h3>

              <div v-if="task.payment_commitments && task.payment_commitments.length" class="overflow-x-auto">
                <table class="w-full text-left text-sm border-collapse">
                  <thead>
                    <tr class="bg-gray-50 border-b border-gray-200">
                      <th class="py-3 px-4 font-semibold text-gray-600">Promise Date</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Amount Promised</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Expected Date</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Status</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Remarks</th>
                      <th class="py-3 px-4 font-semibold text-gray-600 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-200">
                    <tr v-for="c in task.payment_commitments" :key="c.name" class="hover:bg-gray-50/50">
                      <td class="py-3 px-4 text-gray-600">{{ formatDate(c.commitment_date) }}</td>
                      <td class="py-3 px-4 font-semibold text-gray-900">{{ formatCurrency(c.promised_amount) }}</td>
                      <td class="py-3 px-4 text-gray-900 font-medium">{{ formatDate(c.promised_payment_date) }}</td>
                      <td class="py-3 px-4">
                        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold" :class="getCommitmentStatusClass(c.status)">
                          {{ c.status }}
                        </span>
                      </td>
                      <td class="py-3 px-4 text-gray-500 max-w-xs truncate" :title="c.remarks">{{ c.remarks || '—' }}</td>
                      <td class="py-3 px-4 text-right">
                        <div v-if="c.status === 'Pending'" class="inline-flex gap-2">
                          <button
                            @click="updateCommitment(c.name, 'Received')"
                            class="text-xs bg-green-50 hover:bg-green-100 text-green-700 px-2 py-1 rounded font-medium border border-green-200 transition"
                          >
                            Received
                          </button>
                          <button
                            @click="updateCommitment(c.name, 'Not Received')"
                            class="text-xs bg-red-50 hover:bg-red-100 text-red-700 px-2 py-1 rounded font-medium border border-red-200 transition"
                          >
                            Not Paid
                          </button>
                          <button
                            @click="updateCommitment(c.name, 'Cancelled')"
                            class="text-xs bg-gray-50 hover:bg-gray-100 text-gray-600 px-2 py-1 rounded font-medium border border-gray-200 transition"
                          >
                            Cancel
                          </button>
                        </div>
                        <span v-else class="text-xs text-gray-400">Locked</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div v-else class="text-center py-10 text-gray-500 border border-dashed rounded-lg">
                No payment commitments recorded.
              </div>
            </div>

            <!-- TAB 3: RECEIPTS -->
            <div v-if="activeTab === 'receipts'" class="space-y-4">
              <div class="flex items-center justify-between mb-2">
                <h3 class="font-bold text-gray-800">Payment Collection Receipts</h3>
                <Button variant="solid" @click="openReceiptModal" class="bg-green-600 hover:bg-green-700 text-white">
                  <template #prefix><LucideCheck class="h-4 w-4" /></template>
                  Record Receipt
                </Button>
              </div>

              <div v-if="task.payment_receipts && task.payment_receipts.length" class="overflow-x-auto">
                <table class="w-full text-left text-sm border-collapse">
                  <thead>
                    <tr class="bg-gray-50 border-b border-gray-200">
                      <th class="py-3 px-4 font-semibold text-gray-600">Receipt Date</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Amount Received</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Mode</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Ref No.</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Received By</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Remarks</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-200">
                    <tr v-for="(r, idx) in task.payment_receipts" :key="idx" class="hover:bg-gray-50/50">
                      <td class="py-3 px-4 text-gray-600">{{ formatDate(r.receipt_date) }}</td>
                      <td class="py-3 px-4 font-bold text-green-700">{{ formatCurrency(r.amount_received) }}</td>
                      <td class="py-3 px-4 text-gray-800">{{ r.payment_mode }}</td>
                      <td class="py-3 px-4 text-gray-500 font-mono text-xs">{{ r.transaction_reference || '—' }}</td>
                      <td class="py-3 px-4 text-gray-600">{{ getUserFullName(r.received_by) }}</td>
                      <td class="py-3 px-4 text-gray-500">{{ r.remarks || '—' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div v-else class="text-center py-10 text-gray-500 border border-dashed rounded-lg">
                No payments recorded yet. Click "Record Receipt" to register a payment.
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
          <h4 class="text-xs font-bold uppercase tracking-wider text-gray-400">Customer Contact Details</h4>
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

    <!-- DIALOG MODAL: RECORD RECEIPT -->
    <Dialog
      v-model="receiptModalOpen"
      :options="{
        title: 'Record Payment Collection Receipt',
        size: 'xl'
      }"
    >
      <template #body-content>
        <div class="space-y-4 p-1">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Amount Received -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Amount Received (INR) <span class="text-red-500">*</span></label>
              <div class="relative">
                <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm">₹</span>
                <input
                  v-model="receiptForm.amount_received"
                  type="number"
                  placeholder="0"
                  class="w-full rounded-lg border border-gray-300 pl-7 pr-3 py-2 text-sm focus:border-green-500 focus:outline-none font-bold"
                  required
                />
              </div>
            </div>

            <!-- Payment Mode -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Payment Mode <span class="text-red-500">*</span></label>
              <select
                v-model="receiptForm.payment_mode"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-green-500 focus:outline-none"
                required
              >
                <option value="Cash">Cash</option>
                <option value="Bank Transfer">Bank Transfer</option>
                <option value="Cheque">Cheque</option>
                <option value="Online">Online</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <!-- Reference Number -->
            <div class="col-span-1 md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">Transaction Reference (e.g. UTR / Cheque No.)</label>
              <input
                v-model="receiptForm.transaction_reference"
                type="text"
                placeholder="UTR transaction hash, bank reference, or cheque number"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-green-500 focus:outline-none"
              />
            </div>

            <!-- Remarks -->
            <div class="col-span-1 md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">Remarks</label>
              <textarea
                v-model="receiptForm.remarks"
                rows="2"
                placeholder="Remarks about the payment receipt"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-green-500 focus:outline-none"
              ></textarea>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end gap-2 mt-4">
          <Button variant="subtle" @click="receiptModalOpen = false">Close</Button>
          <Button variant="solid" :loading="isReceiptSaving" @click="saveReceipt" class="bg-green-600 text-white hover:bg-green-700">Record Payment</Button>
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
import LucideCheck from "~icons/lucide/check";
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
const activeTab = ref("calls");

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
    const doc = await call("frappe.client.get_doc", {
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
  if (!task.value?.call_history) return [];
  return [...task.value.call_history].sort(
    (a, b) => new Date(b.call_date_and_time).getTime() - new Date(a.call_date_and_time).getTime()
  );
});

function getUserFullName(email: string) {
  return userMap.value[email] || email;
}

// Actions
async function updateStatus() {
  try {
    const doc = await call("frappe.client.set_value", {
      doctype: "Payment Collection Task",
      name: props.taskId,
      fieldname: "status",
      value: task.value.status
    });
    if (doc) {
      // Reload task details to sync amounts and check for status
      await fetchTaskDetails();
    }
  } catch (err: any) {
    console.error("Failed to update status:", err);
    alert(err.message || "Failed to update status. Outstanding balance constraint might apply.");
    // Revert status on UI
    await fetchTaskDetails();
  }
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
    const updatedDoc = await call("test_app.api.log_payment_call", {
      task_id: props.taskId,
      ...callForm.value
    });
    if (updatedDoc) {
      task.value = updatedDoc;
      callModalOpen.value = false;
      await fetchTaskDetails(); // Full sync
    }
  } catch (err: any) {
    console.error("Failed to log call:", err);
    alert(err.message || "Failed to log call.");
  } finally {
    isCallSaving.value = false;
  }
}

// Record Receipt Modal actions
function openReceiptModal() {
  receiptForm.value = {
    amount_received: task.value.outstanding_amount || 0,
    payment_mode: "Bank Transfer",
    transaction_reference: "",
    remarks: ""
  };
  receiptModalOpen.value = true;
}

async function saveReceipt() {
  if (!receiptForm.value.amount_received || receiptForm.value.amount_received <= 0) {
    alert("Please enter a valid amount received.");
    return;
  }
  isReceiptSaving.value = true;
  try {
    const updatedDoc = await call("test_app.api.record_payment_receipt", {
      task_id: props.taskId,
      ...receiptForm.value
    });
    if (updatedDoc) {
      task.value = updatedDoc;
      receiptModalOpen.value = false;
      await fetchTaskDetails(); // Full sync
    }
  } catch (err: any) {
    console.error("Failed to record receipt:", err);
    alert(err.message || "Failed to record receipt.");
  } finally {
    isReceiptSaving.value = false;
  }
}

// Update commitment status
async function updateCommitment(commitmentId: string, status: string) {
  const remarks = prompt(`Enter optional remarks/feedback for marking this promise as ${status}:`);
  try {
    const updatedDoc = await call("test_app.api.update_commitment_status", {
      task_id: props.taskId,
      commitment_row_id: commitmentId,
      status,
      remarks: remarks || ""
    });
    if (updatedDoc) {
      task.value = updatedDoc;
      await fetchTaskDetails(); // Full sync
    }
  } catch (err: any) {
    console.error("Failed to update commitment:", err);
    alert(err.message || "Failed to update commitment status.");
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

function getCommitmentStatusClass(status: string) {
  switch (status) {
    case "Pending":
      return "bg-yellow-100 text-yellow-800 border border-yellow-200";
    case "Received":
      return "bg-green-100 text-green-800 border border-green-200";
    case "Not Received":
      return "bg-red-100 text-red-800 border border-red-200";
    case "Cancelled":
      return "bg-gray-100 text-gray-800 border border-gray-200";
    default:
      return "bg-gray-100 text-gray-800";
  }
}
</script>
