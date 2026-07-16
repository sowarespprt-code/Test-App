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
          <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-0.5">Call Management Task</div>
          <div class="flex items-center gap-3">
            <h1 class="text-2xl font-bold text-gray-900">{{ customerName }} <span class="text-lg text-gray-500 font-normal ml-2">[{{ task.customer_code }}]</span></h1>
            <button v-if="isManager" @click="openCustomerSearch" class="text-blue-500 hover:text-blue-700 text-xs flex items-center gap-1 bg-blue-50 px-2 py-0.5 rounded transition" title="Change Customer">
              <LucideEdit class="w-3.5 h-3.5" /> Edit
            </button>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-3">
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="flex-1 overflow-hidden flex flex-col md:flex-row">
      <!-- Left side: Activity Logs / Tables -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6">
        
        <!-- Contact Info Section -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 mb-6">
          <h4 class="text-sm font-bold uppercase tracking-wider text-gray-500 mb-4 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <LucideUser class="w-4 h-4" /> Customer Contact Details
            </div>
            <Button variant="solid" :loading="isSavingContact" @click="saveContactDetails" class="bg-blue-600 text-white hover:bg-blue-700 text-xs py-1 px-3 h-8">
              Save Changes
            </Button>
          </h4>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <span class="text-gray-500 block text-xs mb-1">Primary Contact</span>
              <input
                v-model="task.contact_person"
                type="text"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 font-semibold text-gray-900 bg-white"
              />
            </div>
            <div>
              <span class="text-gray-500 block text-xs mb-1">Primary Mobile</span>
              <div class="flex gap-2">
                <input
                  v-model="task.mobile_number"
                  type="text"
                  class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 font-bold text-blue-600 bg-white"
                />
              </div>
            </div>
            <div>
              <span class="text-gray-500 block text-xs mb-1">Alternate Mobile</span>
              <div class="flex gap-2">
                <input
                  v-model="task.alternate_mobile"
                  type="text"
                  placeholder="Optional"
                  class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 font-medium text-gray-700 bg-white"
                />
              </div>
            </div>
          </div>
        </div>
        
        <!-- Stat Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex flex-col justify-between">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-gray-500">Total Receivable</span>
            </div>
            <span class="text-2xl font-bold text-gray-900 mt-2">{{ formatCurrency(totalReceivableAmount) }}</span>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex flex-col justify-between">
            <span class="text-sm font-medium text-gray-500">Total Collected</span>
            <span class="text-2xl font-bold text-green-600 mt-2">{{ formatCurrency(totalCollectedAmount) }}</span>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex flex-col justify-between" :class="totalOutstandingAmount > 0 ? 'bg-red-50/20 border-red-100' : ''">
            <span class="text-sm font-medium text-gray-500">Outstanding Balance</span>
            <span class="text-2xl font-extrabold mt-2" :class="totalOutstandingAmount > 0 ? 'text-red-600' : 'text-green-600'">
              {{ formatCurrency(totalOutstandingAmount) }}
            </span>
          </div>
        </div>

        <!-- Pending Tasks for this Customer -->
        <div v-if="allPendingTasks && allPendingTasks.length" class="bg-amber-50 border border-amber-200 rounded-xl overflow-hidden mb-6">
           <div class="px-5 py-4 border-b border-amber-200 flex items-center justify-between bg-amber-100/50">
             <h3 class="font-bold text-amber-900 flex items-center gap-2">
               <LucideListTodo class="w-5 h-5 text-amber-600" />
               Customer Tasks
             </h3>
           </div>
           <div class="overflow-x-auto">
             <table class="w-full text-left border-collapse text-sm">
               <thead>
                 <tr class="bg-amber-50/50 text-amber-800 border-b border-amber-200">
                   <th class="py-3 px-4 font-semibold">Task No & Purpose</th>
                   <th class="py-3 px-4 font-semibold">Description</th>
                   <th class="py-3 px-4 font-semibold">Status & Follow-up</th>
                   <th class="py-3 px-4 font-semibold text-right">Total Amount</th>
                   <th class="py-3 px-4 font-semibold text-right">Collected Amount</th>
                   <th class="py-3 px-4 font-semibold text-right">Balance Amount</th>
                   <th class="py-3 px-4 font-semibold text-center">Action</th>
                 </tr>
               </thead>
               <tbody class="divide-y divide-amber-100">
                 <tr v-for="ot in allPendingTasks" :key="ot.name" class="bg-white hover:bg-amber-50/30 transition-colors" :class="ot.name === task.name ? 'border-l-4 border-l-blue-500' : ''">
                   <td class="py-3 px-4 align-top">
                     <div class="font-bold text-gray-800">{{ ot.name }}</div>
                     <div class="text-sm font-medium text-gray-700 mt-0.5">{{ ot.purpose_type || ot.task_type || 'Call Management Task' }}</div>
                   </td>
                   <td class="py-3 px-4 align-top">
                     <div class="text-xs text-gray-500 whitespace-pre-wrap leading-relaxed max-w-sm">{{ ot.task_description }}</div>
                   </td>
                   <td class="py-3 px-4 align-top">
                     <div class="font-semibold text-gray-700 text-sm">{{ ot.status }}</div>
                     <div v-if="ot.next_follow_up_date" class="mt-1 text-xs text-orange-700 bg-orange-50 px-2 py-0.5 rounded-full inline-block whitespace-nowrap font-medium">
                        Next: {{ formatDate(ot.next_follow_up_date) }}
                     </div>
                   </td>
                   <td class="py-3 px-4 text-right text-gray-900 font-medium whitespace-nowrap align-top">
                     {{ formatCurrency(ot.payment_amount || 0) }}
                   </td>
                   <td class="py-3 px-4 text-right text-green-600 font-medium whitespace-nowrap align-top">
                     {{ formatCurrency(ot.collected_amount || 0) }}
                   </td>
                   <td class="py-3 px-4 text-right text-red-600 font-bold whitespace-nowrap align-top">
                     {{ formatCurrency(ot.outstanding_amount || 0) }}
                   </td>
                    <td class="py-3 px-4 text-center align-top">
                      <div class="flex items-center justify-center gap-1.5 mt-1">
                        <Button variant="solid" :disabled="temporarilyLoggedCalls[ot.name]" class="bg-gray-900 text-white hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed text-xs py-1 px-2 h-7" @click="openLogCallModal(ot.name)">
                          Log Call
                        </Button>
                        <LucideCheckCircle v-if="temporarilyLoggedCalls[ot.name]" class="w-4 h-4 text-green-500" title="Call logged in this session" />
                      </div>
                    </td>
                 </tr>
               </tbody>
             </table>
           </div>
        </div>

        <!-- Tabs Container -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex-1 flex flex-col min-h-[400px]">
          <!-- Tab Headers -->
          <div class="bg-white p-4 border-b border-gray-100 flex overflow-x-auto">
            <div class="flex gap-3">
              <!-- Activity Tab -->
              <button
                @click="activeTab = 'activity'"
                class="px-4 py-2 rounded-full text-sm font-semibold transition-all duration-300 flex items-center gap-2 border whitespace-nowrap"
                :class="activeTab === 'activity' ? 'bg-purple-500 text-white border-purple-600 shadow-md' : 'bg-purple-50 text-purple-600 border-purple-100 hover:bg-purple-100 hover:border-purple-200 hover:text-purple-700'"
              >
                <LucideActivity class="w-4 h-4" /> Activity
              </button>

              <!-- Call History Tab -->
              <button
                @click="activeTab = 'calls'"
                class="px-4 py-2 rounded-full text-sm font-semibold transition-all duration-300 flex items-center gap-2 border whitespace-nowrap"
                :class="activeTab === 'calls' ? 'bg-blue-500 text-white border-blue-600 shadow-md' : 'bg-blue-50 text-blue-600 border-blue-100 hover:bg-blue-100 hover:border-blue-200 hover:text-blue-700'"
              >
                <LucidePhone class="w-4 h-4" /> Call History 
                <span class="px-2 py-0.5 rounded-full text-xs font-bold" :class="activeTab === 'calls' ? 'bg-white/20 text-white' : 'bg-blue-200 text-blue-800'">{{ customerHistory.calls?.length || 0 }}</span>
              </button>

              <!-- Commitments Tab -->
              <button
                @click="activeTab = 'commitments'"
                class="px-4 py-2 rounded-full text-sm font-semibold transition-all duration-300 flex items-center gap-2 border whitespace-nowrap"
                :class="activeTab === 'commitments' ? 'bg-red-500 text-white border-red-600 shadow-md' : 'bg-red-50 text-red-600 border-red-100 hover:bg-red-100 hover:border-red-200 hover:text-red-700'"
              >
                <LucideCalendarClock class="w-4 h-4" /> Payment Commitments
                <span class="px-2 py-0.5 rounded-full text-xs font-bold" :class="activeTab === 'commitments' ? 'bg-white/20 text-white' : 'bg-red-200 text-red-800'">{{ customerHistory.commitments?.length || 0 }}</span>
              </button>

              <!-- Receipts Tab -->
              <button
                @click="activeTab = 'receipts'"
                class="px-4 py-2 rounded-full text-sm font-semibold transition-all duration-300 flex items-center gap-2 border whitespace-nowrap"
                :class="activeTab === 'receipts' ? 'bg-orange-500 text-white border-orange-600 shadow-md' : 'bg-orange-50 text-orange-600 border-orange-100 hover:bg-orange-100 hover:border-orange-200 hover:text-orange-700'"
              >
                <LucideReceipt class="w-4 h-4" /> Receipts & Payments
                <span class="px-2 py-0.5 rounded-full text-xs font-bold" :class="activeTab === 'receipts' ? 'bg-white/20 text-white' : 'bg-orange-200 text-orange-800'">{{ customerHistory.receipts?.length || 0 }}</span>
              </button>
            </div>
          </div>

          <!-- Tab Contents -->
          <div class="p-6 flex-1 overflow-y-auto">
            <!-- TAB 0: ACTIVITY LOG -->
            <div v-if="activeTab === 'activity'" class="h-full">
              <TaskActivityPanel ref="activityPanelRef" doctype="Payment Collection Task" :docname="task.name" />
            </div>

            <!-- TAB 1: CALL HISTORY -->
            <div v-if="activeTab === 'calls'" class="space-y-4">
              <div class="flex items-center justify-between mb-2">
                <h3 class="font-bold text-gray-800">Call Logs</h3>
              </div>

              <div v-if="customerHistory.calls && customerHistory.calls.length" class="space-y-4">
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
                    <div class="flex items-center gap-2">
                      <span class="text-[10px] font-bold text-gray-700 bg-gray-100 px-2 py-0.5 rounded border border-gray-200 uppercase">{{ call.parent }}</span>
                      <span class="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
                        Logged by {{ getUserFullName(call.staff_member) }}
                      </span>
                    </div>
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

              <div v-if="customerHistory.commitments && customerHistory.commitments.length" class="overflow-x-auto">
                <table class="w-full text-left text-sm border-collapse">
                  <thead>
                    <tr class="bg-gray-50 border-b border-gray-200">
                      <th class="py-3 px-4 font-semibold text-gray-600">Task</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Promise Date</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Amount Promised</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Balance Amount</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Expected Date</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Status</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Remarks</th>
                      <th class="py-3 px-4 font-semibold text-gray-600 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-200">
                    <tr v-for="c in sortedCommitments" :key="c.name" class="hover:bg-gray-50/50">
                      <td class="py-3 px-4 text-xs font-bold text-gray-700">{{ c.parent }}</td>
                      <td class="py-3 px-4 text-gray-600">{{ formatDate(c.commitment_date) }}</td>
                      <td class="py-3 px-4 font-semibold text-gray-900">{{ formatCurrency(c.promised_amount) }}</td>
                      <td class="py-3 px-4 font-bold text-red-600">
                        <span v-if="c.status === 'Pending'">{{ formatCurrency(getOutstandingAmount(c.parent)) }}</span>
                        <span v-else class="text-gray-400 font-normal">—</span>
                      </td>
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
                            @click="openReceiptModalForCommitment(c.name, c.promised_amount, false, c.parent)"
                            class="text-xs bg-green-50 hover:bg-green-100 text-green-700 px-2 py-1 rounded font-medium border border-green-200 transition"
                          >
                            Received
                          </button>
                          <button
                            @click="updateCommitment(c.name, 'Not Received', c.parent)"
                            class="text-xs bg-red-50 hover:bg-red-100 text-red-700 px-2 py-1 rounded font-medium border border-red-200 transition"
                          >
                            Not Paid
                          </button>
                          <button
                            @click="openReceiptModalForCommitment(c.name, c.promised_amount, true, c.parent)"
                            class="text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 px-2 py-1 rounded font-medium border border-blue-200 transition"
                          >
                            Partially Paid
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

              <div v-if="customerHistory.receipts && customerHistory.receipts.length" class="overflow-x-auto">
                <table class="w-full text-left text-sm border-collapse">
                  <thead>
                    <tr class="bg-gray-50 border-b border-gray-200">
                      <th class="py-3 px-4 font-semibold text-gray-600">Task</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Receipt Date</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Amount Received</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Mode</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Ref No.</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Received By</th>
                      <th class="py-3 px-4 font-semibold text-gray-600">Remarks</th>
                      <th class="py-3 px-4 font-semibold text-gray-600 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-200">
                    <tr v-for="(r, idx) in customerHistory.receipts" :key="idx" class="hover:bg-gray-50/50">
                      <td class="py-3 px-4 text-xs font-bold text-gray-700">{{ r.parent }}</td>
                      <td class="py-3 px-4 text-gray-600">{{ formatDate(r.receipt_date) }}</td>
                      <td class="py-3 px-4 font-bold text-green-700">{{ formatCurrency(r.amount_received) }}</td>
                      <td class="py-3 px-4 text-gray-800">{{ r.payment_mode }}</td>
                      <td class="py-3 px-4 text-gray-500 font-mono text-xs">{{ r.transaction_reference || '—' }}</td>
                      <td class="py-3 px-4 text-gray-600">{{ getUserFullName(r.received_by) }}</td>
                      <td class="py-3 px-4 text-gray-500">{{ r.remarks || '—' }}</td>
                      <td class="py-3 px-4 text-right">
                        <button v-if="isManager" @click="openEditReceiptModal(r)" class="text-blue-600 hover:bg-blue-50 p-1.5 rounded transition" title="Edit Receipt">
                          <LucideEdit class="w-4 h-4" />
                        </button>
                      </td>
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
          <!-- Task Number Display -->
          <div class="bg-blue-50/50 border border-blue-100 rounded-lg px-4 py-2 flex items-center justify-between">
            <span class="text-sm font-medium text-gray-600">Logging call for Task:</span>
            <span class="text-sm font-bold text-blue-700">{{ currentLogCallTaskId }}</span>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Customer Response -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Customer Response <span class="text-red-500">*</span></label>
              <input
                v-model="callForm.customer_response"
                type="text"
                placeholder="e.g. Promised payment / Asked to call back"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-50 disabled:text-gray-500"
                :disabled="isCallLogReadonly"
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
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-50 disabled:text-gray-500"
                :disabled="isCallLogReadonly"
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
                  type="text"
                  inputmode="decimal"
                  placeholder="0"
                  class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-green-500 focus:outline-none bg-white font-semibold"
                  @input="callForm.promised_amount = $event.target.value.replace(/[^0-9.]/g, '')"
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
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-50 disabled:text-gray-500"
              :disabled="isCallLogReadonly"
              required
            ></textarea>
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end gap-2 mt-4">
          <Button variant="subtle" @click="callModalOpen = false">Close</Button>
          <Button variant="solid" :loading="isCallSaving" @click="saveCallLog" class="bg-blue-600 text-white hover:bg-blue-700">
            {{ isCallLogReadonly ? 'Update Date' : 'Save Call' }}
          </Button>
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
          <!-- Read-only Total Outstanding Balance -->
          <div class="bg-red-50 border border-red-100 rounded-lg p-3 flex justify-between items-center">
            <span class="text-sm font-semibold text-red-800">Total Outstanding Balance (To Be Paid):</span>
            <span class="text-lg font-bold text-red-600">{{ formatCurrency(task?.outstanding_amount || 0) }}</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Amount Received -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Amount Received (INR) <span class="text-red-500">*</span></label>
              <div class="relative">
                <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm">₹</span>
                <input
                  v-model="receiptForm.amount_received"
                  type="text"
                  inputmode="decimal"
                  class="w-full rounded-lg border border-gray-300 pl-7 pr-3 py-2 text-sm focus:border-green-500 focus:outline-none font-bold"
                  :class="{'bg-gray-100 text-gray-500': isReceiptAmountReadonly}"
                  :readonly="isReceiptAmountReadonly"
                  @input="receiptForm.amount_received = $event.target.value.replace(/[^0-9.]/g, '')"
                  required
                />
              </div>
            </div>

            <!-- Payment Mode -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Payment Mode <span class="text-red-500">*</span></label>
              <select
                v-model="receiptForm.payment_mode"
                @change="handlePaymentModeChange"
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
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Transaction Reference (e.g. UTR / Cheque No.)
                <span v-if="receiptForm.payment_mode !== 'Cash'" class="text-red-500">*</span>
              </label>
              <input
                v-model="receiptForm.transaction_reference"
                type="text"
                placeholder="UTR transaction hash, bank reference, or cheque number"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-green-500 focus:outline-none"
                :class="{'bg-gray-100 text-gray-400': receiptForm.payment_mode === 'Cash'}"
                :disabled="receiptForm.payment_mode === 'Cash'"
                :required="receiptForm.payment_mode !== 'Cash'"
              />
            </div>

            <!-- Next Follow-up Date -->
            <div class="col-span-1 md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Next Follow-up Date
                <span v-if="Number(receiptForm.amount_received || 0) >= Number(task?.outstanding_amount || 0)" class="text-gray-500 font-normal ml-1">(Optional)</span>
                <span v-else class="text-red-500">*</span>
              </label>
              <input
                v-model="receiptForm.next_follow_up_date"
                type="date"
                :required="Number(receiptForm.amount_received || 0) < Number(task?.outstanding_amount || 0)"
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

    <!-- DIALOG MODAL: EDIT TASK -->
    <Dialog
      v-model="editTaskModalOpen"
      :options="{
        title: 'Edit Task Details',
        size: 'xl'
      }"
    >
      <template #body-content>
        <div class="space-y-4 p-1">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Payment Amount (INR)</label>
              <input v-model="editTaskForm.payment_amount" type="text" inputmode="decimal" @input="editTaskForm.payment_amount = $event.target.value.replace(/[^0-9.]/g, '')" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Priority</label>
              <select v-model="editTaskForm.priority" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none bg-white">
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
                <option value="Urgent">Urgent</option>
              </select>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end gap-2 mt-4">
          <Button variant="subtle" @click="editTaskModalOpen = false">Cancel</Button>
          <Button variant="solid" :loading="isTaskSaving" @click="saveEditTask" class="bg-blue-600 text-white hover:bg-blue-700">Save Changes</Button>
        </div>
      </template>
    </Dialog>

    <!-- DIALOG MODAL: EDIT RECEIPT -->
    <Dialog
      v-model="editReceiptModalOpen"
      :options="{
        title: 'Edit Payment Receipt',
        size: 'xl'
      }"
    >
      <template #body-content>
        <div class="space-y-4 p-1">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Amount Received (INR)</label>
              <input v-model="editReceiptForm.amount_received" type="text" inputmode="decimal" @input="editReceiptForm.amount_received = $event.target.value.replace(/[^0-9.]/g, '')" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Payment Mode</label>
              <select v-model="editReceiptForm.payment_mode" @change="handleEditPaymentModeChange" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none bg-white">
                <option value="Cash">Cash</option>
                <option value="Bank Transfer">Bank Transfer</option>
                <option value="Cheque">Cheque</option>
                <option value="Online">Online</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div class="col-span-1 md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">Transaction Reference</label>
              <input v-model="editReceiptForm.transaction_reference" type="text" :class="{'bg-gray-100 text-gray-400': editReceiptForm.payment_mode === 'Cash'}" :disabled="editReceiptForm.payment_mode === 'Cash'" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
            </div>
            <div class="col-span-1 md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">Remarks</label>
              <textarea v-model="editReceiptForm.remarks" rows="2" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"></textarea>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end gap-2 mt-4">
          <Button variant="subtle" @click="editReceiptModalOpen = false">Cancel</Button>
          <Button variant="solid" :loading="isReceiptEditing" @click="saveEditReceipt" class="bg-blue-600 text-white hover:bg-blue-700">Save Changes</Button>
        </div>
      </template>
    </Dialog>

    <!-- Customer Search Popup Modal -->
    <Teleport to="body">
      <CustomerSearchPopup
        v-if="showCustomerSearch"
        v-model="showCustomerSearch"
        @customerSelected="handleCustomerSelected"
      />
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import LucideActivity from "~icons/lucide/activity";
import LucideCalendarClock from "~icons/lucide/calendar-clock";
import LucideReceipt from "~icons/lucide/receipt";
import LucideChevronLeft from "~icons/lucide/chevron-left";
import LucideChevronRight from "~icons/lucide/chevron-right";
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { call, Button, Badge, Dialog } from "frappe-ui";
import LucideArrowLeft from "~icons/lucide/arrow-left";
import LucideUser from "~icons/lucide/user";
import LucidePhoneCall from "~icons/lucide/phone-call";
import LucidePlus from "~icons/lucide/plus";
import LucideCheck from "~icons/lucide/check";
import LucideCheckCircle from "~icons/lucide/check-circle";

import LucidePhone from "~icons/lucide/phone";
import LucideCalendar from "~icons/lucide/calendar";
import LucideTrash2 from "~icons/lucide/trash-2";
import LucideEdit from "~icons/lucide/edit";
import CustomerSearchPopup from "@/components/CustomerSearchPopup.vue";
import TaskActivityPanel from "@/components/TaskActivityPanel.vue";
import LucideBan from "~icons/lucide/ban";
import { useAuthStore } from "@/stores/auth";

const props = defineProps({
  taskId: {
    type: String,
    required: true
  }
});

const router = useRouter();
const { isManager } = useAuthStore();
const task = ref<any>(null);
const customerName = ref("");
const otherPendingTasks = ref<any[]>([]);
const customerHistory = ref<any>({ calls: [], commitments: [], receipts: [] });
const activeTab = ref("calls");
const activityPanelRef = ref(null);

const sortedCommitments = computed(() => {
  if (!customerHistory.value.commitments) return [];
  return [...customerHistory.value.commitments].sort((a, b) => {
    // Keep pending commitments on top
    if (a.status === "Pending" && b.status !== "Pending") return -1;
    if (b.status === "Pending" && a.status !== "Pending") return 1;
    // Then sort by date ascending
    return new Date(a.commitment_date).getTime() - new Date(b.commitment_date).getTime();
  });
});

const allPendingTasks = computed(() => {
  if (!task.value) return otherPendingTasks.value || [];
  return [task.value, ...(otherPendingTasks.value || [])];
});

const totalReceivableAmount = computed(() => {
  return allPendingTasks.value.reduce((sum, t) => sum + (Number(t.payment_amount) || 0), 0);
});

const totalCollectedAmount = computed(() => {
  return allPendingTasks.value.reduce((sum, t) => sum + (Number(t.collected_amount) || 0), 0);
});

const totalOutstandingAmount = computed(() => {
  return allPendingTasks.value.reduce((sum, t) => sum + (Number(t.outstanding_amount) || 0), 0);
});

function getOutstandingAmount(taskId: string) {
  const targetTask = allPendingTasks.value.find(t => t.name === taskId);
  return targetTask ? targetTask.outstanding_amount : 0;
}

const isRightSidebarCollapsed = ref(false);

// Cache maps
const userMap = ref<Record<string, string>>({});
const isSavingContact = ref(false);

async function saveContactDetails() {
  if (!task.value) return;
  isSavingContact.value = true;
  try {
    await call("test_app.api.update_customer_contact_details", {
      customer: task.value.customer,
      contact_person: task.value.contact_person,
      mobile_number: task.value.mobile_number,
      alternate_mobile: task.value.alternate_mobile
    });
    alert("Contact details saved successfully for all pending tasks of this customer.");
    await fetchTaskDetails();
  } catch (err: any) {
    console.error("Failed to save contact details:", err);
    alert(err.message || "Failed to save contact details.");
  } finally {
    isSavingContact.value = false;
  }
}



// Log Call Modal state
const callModalOpen = ref(false);
const isCallSaving = ref(false);
const isCallLogReadonly = ref(false);
const temporarilyLoggedCalls = ref<Record<string, boolean>>({});
const existingCallLogId = ref("");
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
const isReceiptAmountReadonly = ref(false);
const receiptForm = ref({
  amount_received: 0 as number | string,
  payment_mode: "Bank Transfer",
  transaction_reference: "",
  remarks: "",
  next_follow_up_date: "",
  commitment_row_id: "",
  commitment_status: ""
});

const editTaskModalOpen = ref(false);
const isTaskSaving = ref(false);
const editTaskForm = ref({
  purpose_type: "",
  payment_amount: 0,
  priority: "",
  assigned_to: "",
  task_description: ""
});

const editReceiptModalOpen = ref(false);
const isReceiptEditing = ref(false);
const editReceiptForm = ref({
  receipt_row_id: "",
  amount_received: 0 as number | string,
  payment_mode: "",
  transaction_reference: "",
  remarks: ""
});

onMounted(async () => {
  await fetchTaskDetails();
  await fetchUsers();

  // Log the view for activity tracker
  call("test_app.api.timeline.log_view", {
    doctype: "Payment Collection Task",
    docname: props.taskId
  }).catch(() => {});
});

async function fetchTaskDetails() {
  try {
    const doc = await call("frappe.client.get", {
      doctype: "Payment Collection Task",
      name: props.taskId
    });
    task.value = doc;

    // Fetch customer display name and other pending tasks
    if (doc.customer) {
      const cust = await call("frappe.client.get_value", {
        doctype: "HD Customer",
        filters: { name: doc.customer },
        fieldname: "customer_name"
      });
      customerName.value = cust?.customer_name || doc.customer;

      try {
        const otherTasks = await call("test_app.api.get_customer_pending_tasks", {
          customer: doc.customer,
          current_task_id: props.taskId
        });
        otherPendingTasks.value = otherTasks || [];
        const history = await call("test_app.api.get_customer_history", {
          customer: doc.customer
        });
        customerHistory.value = history || { calls: [], commitments: [], receipts: [] };
      } catch(e) {
        console.error("Failed to fetch other tasks or history", e);
      }
    }
  } catch (err) {
    console.error("Failed to load task details:", err);
    alert("Failed to load call management task details.");
  } finally {
    if (activityPanelRef.value) {
      // @ts-ignore
      activityPanelRef.value.fetchActivities();
    }
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
  if (!customerHistory.value.calls) return [];
  return [...customerHistory.value.calls].sort(
    (a, b) => new Date(b.call_date_and_time).getTime() - new Date(a.call_date_and_time).getTime()
  );
});

function getUserFullName(email: string) {
  return userMap.value[email] || email;
}

async function cancelTask() {
  if (!confirm("Are you sure you want to cancel this Call Management Task? This will also cancel all pending commitments.")) return;
  try {
    await call("test_app.api.cancel_task", { doctype: "Call Management Task", task_id: props.taskId });
    await fetchTaskDetails();
  } catch (err: any) {
    console.error("Failed to cancel task:", err);
    alert(err.message || "Failed to cancel task.");
  }
}

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

async function updateField(fieldname: string, value: any) {
  try {
    await call("frappe.client.set_value", {
      doctype: "Payment Collection Task",
      name: props.taskId,
      fieldname,
      value
    });
    await fetchTaskDetails();
  } catch (err: any) {
    console.error(`Failed to update ${fieldname}:`, err);
    alert(err.message || `Failed to update ${fieldname}.`);
    await fetchTaskDetails();
  }
}

function openCustomerSearch() {
  if (isManager) showCustomerSearch.value = true;
}

async function handleCustomerSelected(customer: any) {
  await updateField("customer", customer.name);
  showCustomerSearch.value = false;
}

// Log Call Modal actions
const currentLogCallTaskId = ref("");

function openLogCallModal(targetTaskId: string) {
  currentLogCallTaskId.value = targetTaskId || props.taskId;
  isCallLogReadonly.value = false;
  existingCallLogId.value = "";
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
  if (!isCallLogReadonly.value && (!callForm.value.customer_response || !callForm.value.discussion_summary)) {
    alert("Please fill in the customer response and discussion summary.");
    return;
  }
  isCallSaving.value = true;
  try {
    if (isCallLogReadonly.value) {
      await call("test_app.api.update_task_follow_up_date", {
        task_id: currentLogCallTaskId.value,
        call_log_id: existingCallLogId.value,
        next_follow_up_date: callForm.value.next_follow_up_date
      });
    } else {
      await call("test_app.api.log_management_call", {
        task_id: currentLogCallTaskId.value,
        ...callForm.value
      });
    }
    callModalOpen.value = false;
    
    // Only update local state if we logged call for the currently viewed task
    if (currentLogCallTaskId.value === task.value?.name && task.value.status === 'Open') {
      task.value.status = 'In Progress';
    }
    
    temporarilyLoggedCalls.value[currentLogCallTaskId.value] = true;
    await fetchTaskDetails(); // Full sync
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
    remarks: "",
    next_follow_up_date: "",
    commitment_row_id: "",
    commitment_status: ""
  };
  isReceiptAmountReadonly.value = false;
  receiptModalOpen.value = true;
}

function openReceiptModalForCommitment(commitmentId: string, promisedAmount: number, isPartial: boolean, parentTask: string = "") {
  receiptForm.value = {
    amount_received: isPartial ? '' : promisedAmount,
    payment_mode: "Bank Transfer",
    transaction_reference: "",
    remarks: "",
    next_follow_up_date: "",
    commitment_row_id: commitmentId,
    commitment_status: isPartial ? "Partially Paid" : "Received",
    target_task_id: parentTask
  };
  isReceiptAmountReadonly.value = !isPartial;
  receiptModalOpen.value = true;
}

function handlePaymentModeChange() {
  if (receiptForm.value.payment_mode === 'Cash') {
    receiptForm.value.transaction_reference = "";
  }
}

function handleEditPaymentModeChange() {
  if (editReceiptForm.value.payment_mode === 'Cash') {
    editReceiptForm.value.transaction_reference = "";
  }
}

async function saveReceipt() {
  if (!receiptForm.value.amount_received || Number(receiptForm.value.amount_received) <= 0) {
    alert("Please enter a valid amount received.");
    return;
  }
  if (receiptForm.value.payment_mode !== 'Cash' && (!receiptForm.value.transaction_reference || !receiptForm.value.transaction_reference.trim())) {
    alert(`Transaction Reference is mandatory for ${receiptForm.value.payment_mode} payments.`);
    return;
  }
  if (Number(receiptForm.value.amount_received) > task.value.outstanding_amount) {
    alert("Amount received cannot be greater than the outstanding payable amount.");
    return;
  }
  isReceiptSaving.value = true;
  try {
    const updatedDoc = await call("test_app.api.record_payment_receipt", {
      task_id: receiptForm.value.target_task_id || props.taskId,
      ...receiptForm.value
    });
    if (updatedDoc) {
      task.value = updatedDoc;
      receiptModalOpen.value = false;
      await fetchTaskDetails(); // Full sync
    }
  } catch (err: any) {
    console.error("Failed to record receipt:", err);
    const errorMsg = (err.messages && err.messages.length > 0 && err.messages[0] !== err.message) ? err.messages[0] : (err.message || "Failed to record receipt.");
    alert(errorMsg);
  } finally {
    isReceiptSaving.value = false;
  }
}

// Update commitment status
async function updateCommitment(commitmentId: string, status: string, parentTask: string = "") {
  const remarks = prompt(`Enter optional remarks/feedback for marking this promise as ${status}:`);
  if (remarks === null) return; // User cancelled the prompt
  
  try {
    const updatedDoc = await call("test_app.api.update_commitment_status", {
      task_id: parentTask || props.taskId,
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

function openEditTaskModal() {
  if (!task.value) return;
  editTaskForm.value = {
    purpose_type: task.value.purpose_type || "Software Payment",
    payment_amount: task.value.payment_amount || 0,
    priority: task.value.priority || "Medium",
    assigned_to: task.value.assigned_to || "",
    task_description: task.value.task_description || ""
  };
  editTaskModalOpen.value = true;
}

async function saveEditTask() {
  isTaskSaving.value = true;
  try {
    const updatedDoc = await call("test_app.api.update_task_details", {
      task_id: props.taskId,
      updates: JSON.stringify(editTaskForm.value)
    });
    if (updatedDoc) {
      task.value = updatedDoc;
      editTaskModalOpen.value = false;
    }
  } catch (error) {
    console.error("Failed to update task details:", error);
    alert("Failed to update task details. Check console for error.");
  } finally {
    isTaskSaving.value = false;
  }
}

function openEditReceiptModal(receipt: any) {
  editReceiptForm.value = {
    receipt_row_id: receipt.name,
    amount_received: receipt.amount_received || 0,
    payment_mode: receipt.payment_mode || "Bank Transfer",
    transaction_reference: receipt.transaction_reference || "",
    remarks: receipt.remarks || "",
    original_amount: receipt.amount_received || 0
  };
  editReceiptModalOpen.value = true;
}

async function saveEditReceipt() {
  const newAmount = Number(editReceiptForm.value.amount_received || 0);
  const maxAllowed = Number(task.value.outstanding_amount || 0) + Number(editReceiptForm.value.original_amount || 0);
  
  if (newAmount > maxAllowed) {
    alert("Amount received cannot make the total collected greater than the total receivable.");
    return;
  }
  if (editReceiptForm.value.payment_mode !== 'Cash' && (!editReceiptForm.value.transaction_reference || !editReceiptForm.value.transaction_reference.trim())) {
    alert(`Transaction Reference is mandatory for ${editReceiptForm.value.payment_mode} payments.`);
    return;
  }

  isReceiptEditing.value = true;
  try {
    const updatedDoc = await call("test_app.api.update_receipt_details", {
      task_id: props.taskId,
      receipt_row_id: editReceiptForm.value.receipt_row_id,
      updates: JSON.stringify({
        amount_received: editReceiptForm.value.amount_received,
        payment_mode: editReceiptForm.value.payment_mode,
        transaction_reference: editReceiptForm.value.transaction_reference,
        remarks: editReceiptForm.value.remarks
      })
    });
    if (updatedDoc) {
      task.value = updatedDoc;
      editReceiptModalOpen.value = false;
      await fetchTaskDetails(); // Re-fetch to ensure all properties sync correctly
    }
  } catch (error: any) {
    console.error("Failed to update receipt details:", error);
    const errorMsg = (error.messages && error.messages.length > 0 && error.messages[0] !== error.message) ? error.messages[0] : (error.message || "Failed to update receipt details.");
    alert(errorMsg);
  } finally {
    isReceiptEditing.value = false;
  }
}
</script>
