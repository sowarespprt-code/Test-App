<template>
  <div class="h-full flex flex-col bg-gray-50 overflow-hidden relative p-4">
    <div class="mb-4 flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-800">Accounts: Payment Commitments & Receipts</h1>
      
      <div class="flex gap-2">
         <select v-model="statusFilter" class="rounded-lg border-gray-300 text-sm p-2">
            <option value="">All Statuses</option>
            <option value="Pending">Pending</option>
            <option value="Received">Received</option>
            <option value="Partially Paid">Partially Paid</option>
            <option value="Not Received">Not Received</option>
         </select>
      </div>
    </div>
    
    <div class="flex gap-4 border-b border-gray-200 mb-4">
      <button 
        @click="activeTab = 'commitments'" 
        :class="activeTab === 'commitments' ? 'border-b-2 border-indigo-600 text-indigo-600 font-bold' : 'text-gray-500'"
        class="pb-2 px-4 transition"
      >
        Commitments ({{ filteredCommitments.length }})
      </button>
      <button 
        @click="activeTab = 'receipts'" 
        :class="activeTab === 'receipts' ? 'border-b-2 border-indigo-600 text-indigo-600 font-bold' : 'text-gray-500'"
        class="pb-2 px-4 transition"
      >
        Receipts ({{ receipts.length }})
      </button>
    </div>

    <!-- Commitments Table -->
    <div v-if="activeTab === 'commitments'" class="bg-white rounded-xl shadow-sm border border-gray-200 flex-1 overflow-auto">
      <table class="w-full text-left text-sm whitespace-nowrap">
        <thead class="bg-gray-100/50">
          <tr>
            <th class="py-3 px-4 font-semibold text-gray-600">Task / Customer</th>
            <th class="py-3 px-4 font-semibold text-gray-600">Total Receivable</th>
            <th class="py-3 px-4 font-semibold text-gray-600">Promised Amount</th>
            <th class="py-3 px-4 font-semibold text-gray-600">Collected Amount</th>
            <th class="py-3 px-4 font-semibold text-gray-600">Outstanding Amount</th>
            <th class="py-3 px-4 font-semibold text-gray-600">Expected Date</th>
            <th class="py-3 px-4 font-semibold text-gray-600">Status</th>
            <th class="py-3 px-4 font-semibold text-gray-600 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="c in filteredCommitments" :key="c.name" class="hover:bg-gray-50/50 transition">
            <td class="py-3 px-4">
               <div class="font-medium text-indigo-600 hover:underline cursor-pointer" @click="goToTask(c.task)">{{ c.task }}</div>
               <div class="text-xs text-gray-500 mt-0.5 whitespace-normal max-w-xs break-words">{{ c.customer }}</div>
            </td>
            <td class="py-3 px-4 font-bold text-gray-800">{{ formatCurrency(c.payment_amount) }}</td>
            <td class="py-3 px-4 font-bold text-gray-800">{{ formatCurrency(c.promised_amount) }}</td>
            <td class="py-3 px-4 font-bold text-green-700">{{ formatCurrency(c.collected_amount) }}</td>
            <td class="py-3 px-4 font-bold text-red-600">{{ formatCurrency(c.outstanding_amount) }}</td>
            <td class="py-3 px-4 text-gray-600 font-medium">{{ formatDate(c.promised_payment_date) || '-' }}</td>
            <td class="py-3 px-4">
               <span class="px-2 py-0.5 rounded-full text-xs font-medium" :class="getStatusClass(c.status)">
                 {{ c.status }}
               </span>
            </td>
            <td class="py-3 px-4 text-right">
               <div class="flex items-center justify-end gap-1">
                 <button @click="openEditCommitmentModal(c)" class="text-blue-600 hover:bg-blue-50 p-1 rounded transition" title="Edit Commitment">
                   <LucideEdit class="w-4 h-4" />
                 </button>
                 <template v-if="c.status === 'Pending' || c.status === 'Partially Paid'">
                   <button
                     @click="openReceiptModalForCommitment(c, false)"
                     class="text-[11px] bg-green-50 hover:bg-green-100 text-green-700 px-1.5 py-1 rounded font-medium border border-green-200 transition"
                   >
                     Received
                   </button>
                   <button
                     @click="openReceiptModalForCommitment(c, true)"
                     class="text-[11px] bg-blue-50 hover:bg-blue-100 text-blue-700 px-1.5 py-1 rounded font-medium border border-blue-200 transition"
                   >
                     Partial
                   </button>
                 </template>
                 <span v-else class="text-xs text-gray-400">Locked</span>
               </div>
            </td>
          </tr>
          <tr v-if="!filteredCommitments.length">
             <td colspan="6" class="py-8 text-center text-gray-500">No commitments found</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Receipts Table -->
    <div v-if="activeTab === 'receipts'" class="bg-white rounded-xl shadow-sm border border-gray-200 flex-1 overflow-auto">
      <table class="w-full text-left text-sm whitespace-nowrap">
        <thead class="bg-gray-100/50">
          <tr>
            <th class="py-3 px-4 font-semibold text-gray-600">Task / Customer</th>
            <th class="py-3 px-4 font-semibold text-gray-600">Receipt Date</th>
            <th class="py-3 px-4 font-semibold text-gray-600">Amount Received</th>
            <th class="py-3 px-4 font-semibold text-gray-600">Payment Mode</th>
            <th class="py-3 px-4 font-semibold text-gray-600">Reference</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="r in receipts" :key="r.name" class="hover:bg-gray-50/50 transition">
            <td class="py-3 px-4">
               <div class="font-medium text-indigo-600 hover:underline cursor-pointer" @click="goToTask(r.task)">{{ r.task }}</div>
               <div class="text-xs text-gray-500 mt-0.5">{{ r.customer }}</div>
            </td>
            <td class="py-3 px-4 text-gray-600">{{ formatDate(r.receipt_date) }}</td>
            <td class="py-3 px-4 font-bold text-green-600">{{ formatCurrency(r.amount_received) }}</td>
            <td class="py-3 px-4 text-gray-600">{{ r.payment_mode || '-' }}</td>
            <td class="py-3 px-4 text-gray-600">{{ r.transaction_reference || '-' }}</td>
          </tr>
          <tr v-if="!receipts.length">
             <td colspan="5" class="py-8 text-center text-gray-500">No receipts found</td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Record Payment Modal -->
    <Dialog v-model="showReceiptModal" :options="{ title: 'Record Payment Collection Receipt', size: '2xl' }">
      <template #body-content>
        <div class="space-y-4 p-2">
           <div class="bg-blue-50/50 border border-blue-100 rounded-lg p-3 text-sm text-blue-800">
              Recording payment for Task: <span class="font-bold cursor-pointer hover:underline" @click="goToTask(selectedCommitment?.task)">{{ selectedCommitment?.task }}</span><br/>
              Customer: <span class="font-medium">{{ selectedCommitment?.customer }}</span><br/>
              Outstanding Amount: <span class="font-bold">{{ formatCurrency(selectedCommitment?.outstanding_amount) }}</span>
           </div>
           
           <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
             <div>
               <label class="block text-sm font-semibold text-gray-700 mb-1">Amount Received (INR) <span class="text-red-500">*</span></label>
               <input v-model="receiptForm.amount_received" type="text" inputmode="decimal" @input="receiptForm.amount_received = $event.target.value.replace(/[^0-9.]/g, '')" :disabled="!isPartialReceipt" :class="{'bg-gray-100 text-gray-500': !isPartialReceipt}" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100" />
             </div>
             <div>
                <label class="block text-sm font-semibold text-gray-700 mb-1">Payment Mode <span class="text-red-500">*</span></label>
                <select v-model="receiptForm.payment_mode" @change="handlePaymentModeChange" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100 bg-white">
                  <option value="Bank Transfer">Bank Transfer</option>
                  <option value="UPI">UPI</option>
                  <option value="Cheque">Cheque</option>
                  <option value="Cash">Cash</option>
                </select>
             </div>
             <div v-if="receiptForm.payment_mode !== 'Cash'">
                <label class="block text-sm font-semibold text-gray-700 mb-1">Reference Number <span class="text-red-500">*</span></label>
                <input v-model="receiptForm.transaction_reference" type="text" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100" />
             </div>
             <div v-if="isPartialReceipt">
                <label class="block text-sm font-semibold text-gray-700 mb-1">Next Follow-up Date <span class="text-red-500">*</span></label>
                <input v-model="receiptForm.next_follow_up_date" type="date" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100" />
             </div>
             <div class="md:col-span-2">
                <label class="block text-sm font-semibold text-gray-700 mb-1">Remarks</label>
                <textarea v-model="receiptForm.remarks" rows="2" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"></textarea>
             </div>
           </div>
        </div>
      </template>
      <template #actions>
         <div class="flex justify-end gap-2 mt-4">
           <Button variant="subtle" @click="showReceiptModal = false">Cancel</Button>
           <Button variant="solid" :loading="isSaving" @click="saveReceipt" class="bg-green-600 text-white hover:bg-green-700 shadow-sm">Record Payment</Button>
         </div>
      </template>
    </Dialog>

    <!-- Edit Commitment Modal -->
    <Dialog v-model="showEditCommitmentModal" :options="{ title: 'Edit Payment Commitment', size: '2xl' }">
      <template #body-content>
        <div class="space-y-4 p-2">
           <div class="bg-blue-50/50 border border-blue-100 rounded-lg p-3 text-sm text-blue-800">
              Editing commitment for Task: <span class="font-bold cursor-pointer hover:underline" @click="goToTask(selectedCommitment?.task)">{{ selectedCommitment?.task }}</span><br/>
              Customer: <span class="font-medium">{{ selectedCommitment?.customer }}</span>
           </div>
           
           <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
             <div>
               <label class="block text-sm font-semibold text-gray-700 mb-1">Promised Amount (INR) <span class="text-red-500">*</span></label>
               <input v-model="editCommitmentForm.promised_amount" type="text" inputmode="decimal" @input="editCommitmentForm.promised_amount = $event.target.value.replace(/[^0-9.]/g, '')" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100" />
             </div>
             <div>
                <label class="block text-sm font-semibold text-gray-700 mb-1">Expected Date</label>
                <input v-model="editCommitmentForm.expected_date" type="date" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100" />
             </div>
             <div>
                <label class="block text-sm font-semibold text-gray-700 mb-1">Next Follow-up Date (Task)</label>
                <input v-model="editCommitmentForm.next_follow_up_date" type="date" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100" />
             </div>
           </div>
        </div>
      </template>
      <template #actions>
         <div class="flex justify-end gap-2 mt-4">
           <Button variant="subtle" @click="showEditCommitmentModal = false">Cancel</Button>
           <Button variant="solid" :loading="isEditing" @click="saveEditCommitment" class="bg-blue-600 text-white hover:bg-blue-700 shadow-sm">Save Changes</Button>
         </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import LucideEdit from "~icons/lucide/edit";
import { ref, computed, onMounted } from "vue";
import { Dialog, Button, call, toast } from "frappe-ui";
import { useRouter } from "vue-router";

const router = useRouter();
const commitments = ref<any[]>([]);
const receipts = ref<any[]>([]);
const activeTab = ref("commitments");
const statusFilter = ref("");
const isLoading = ref(false);

const showReceiptModal = ref(false);
const showEditCommitmentModal = ref(false);
const isSaving = ref(false);
const isEditing = ref(false);
const selectedCommitment = ref<any>(null);
const isPartialReceipt = ref(false);

const editCommitmentForm = ref({
  promised_amount: "",
  expected_date: "",
  next_follow_up_date: ""
});

const receiptForm = ref({
  amount_received: "",
  payment_mode: "Bank Transfer",
  transaction_reference: "",
  next_follow_up_date: "",
  remarks: "",
  commitment_row_id: "",
  commitment_status: "",
  target_task_id: ""
});

const isPartial = computed(() => {
  const amount = Number(receiptForm.value.amount_received || 0);
  const outstanding = Number(selectedCommitment.value?.outstanding_amount || 0);
  return amount < outstanding;
});

const filteredCommitments = computed(() => {
  let list = [...commitments.value];
  if (statusFilter.value) {
    list = list.filter(c => c.status === statusFilter.value);
  }
  
  return list.sort((a, b) => {
    const aIsActive = (a.status === 'Pending' || a.status === 'Partially Paid') ? 1 : 0;
    const bIsActive = (b.status === 'Pending' || b.status === 'Partially Paid') ? 1 : 0;
    
    if (aIsActive !== bIsActive) {
      return bIsActive - aIsActive;
    }
    
    const dateA = a.promised_payment_date ? new Date(a.promised_payment_date).getTime() : 0;
    const dateB = b.promised_payment_date ? new Date(b.promised_payment_date).getTime() : 0;
    
    return dateB - dateA;
  });
});

async function fetchData() {
  isLoading.value = true;
  try {
    const res = await call("test_app.api.get_all_commitments_and_receipts");
    commitments.value = res.commitments || [];
    receipts.value = res.receipts || [];
  } catch(e) {
    console.error(e);
  } finally {
    isLoading.value = false;
  }
}

function handlePaymentModeChange() {
  if (receiptForm.value.payment_mode === 'Cash') {
    receiptForm.value.transaction_reference = '';
  }
}

function openReceiptModalForCommitment(c: any, partial: boolean) {
  selectedCommitment.value = c;
  isPartialReceipt.value = partial;
  receiptForm.value = {
    amount_received: partial ? "" : String(c.promised_amount),
    payment_mode: "Bank Transfer",
    transaction_reference: "",
    next_follow_up_date: "",
    remarks: "",
    commitment_row_id: c.name,
    commitment_status: partial ? "Partially Paid" : "Received",
    target_task_id: c.task
  };
  showReceiptModal.value = true;
}

function openEditCommitmentModal(c: any) {
  selectedCommitment.value = c;
  editCommitmentForm.value = {
    promised_amount: c.promised_amount ? String(c.promised_amount) : "",
    expected_date: c.promised_payment_date || "",
    next_follow_up_date: c.task_next_follow_up_date || ""
  };
  showEditCommitmentModal.value = true;
}

async function saveEditCommitment() {
  const amt = Number(editCommitmentForm.value.promised_amount);
  if (amt <= 0) {
    alert("Please enter a valid amount.");
    return;
  }
  
  isEditing.value = true;
  try {
    await call("test_app.api.edit_commitment", {
      task_id: selectedCommitment.value.task,
      commitment_row_id: selectedCommitment.value.name,
      promised_amount: amt,
      expected_date: editCommitmentForm.value.expected_date || null,
      next_follow_up_date: editCommitmentForm.value.next_follow_up_date || null
    });
    toast.success("Commitment updated successfully");
    showEditCommitmentModal.value = false;
    await fetchData();
  } catch (err: any) {
    const errorMsg = (err.messages && err.messages.length > 0 && err.messages[0] !== err.message) ? err.messages[0] : (err.message || "Failed to edit commitment.");
    alert(errorMsg);
  } finally {
    isEditing.value = false;
  }
}

async function saveReceipt() {
  const amt = Number(receiptForm.value.amount_received);
  if (amt <= 0) {
    alert("Please enter a valid amount.");
    return;
  }
  if (receiptForm.value.payment_mode !== 'Cash' && !receiptForm.value.transaction_reference.trim()) {
    alert("Please enter a reference number.");
    return;
  }
  if (isPartialReceipt.value && !receiptForm.value.next_follow_up_date) {
    alert("Please select the next follow up date for the remaining balance.");
    return;
  }
  const outstanding = Number(selectedCommitment.value?.outstanding_amount || 0);
  if (amt > outstanding) {
    alert(`Amount received cannot be greater than the task's outstanding amount (₹${outstanding}).`);
    return;
  }
  
  isSaving.value = true;
  try {
    await call("test_app.api.record_payment_receipt", {
      task_id: selectedCommitment.value.task,
      ...receiptForm.value,
      commitment_row_id: selectedCommitment.value.name,
      commitment_status: amt >= outstanding ? 'Received' : 'Partially Paid'
    });
    toast.success("Payment recorded successfully");
    showReceiptModal.value = false;
    await fetchData();
  } catch (err: any) {
    const errorMsg = (err.messages && err.messages.length > 0 && err.messages[0] !== err.message) ? err.messages[0] : (err.message || "Failed to record receipt.");
    alert(errorMsg);
  } finally {
    isSaving.value = false;
  }
}

function goToTask(taskId: string) {
  if (taskId) {
    showReceiptModal.value = false;
    router.push({ name: "PaymentCollectionTaskDetail", params: { taskId: taskId } });
  }
}

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

function getStatusClass(status: string) {
  switch (status) {
    case 'Received': return 'bg-green-100 text-green-800';
    case 'Pending': return 'bg-yellow-100 text-yellow-800 border border-yellow-200';
    case 'Partially Paid': return 'bg-blue-100 text-blue-800 border border-blue-200';
    case 'Not Received': return 'bg-red-100 text-red-800';
    case 'Cancelled': return 'bg-gray-100 text-gray-800';
    default: return 'bg-gray-100 text-gray-800';
  }
}

onMounted(() => {
  fetchData();
});
</script>
