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
          <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-0.5">Payment Task</div>
          <div class="flex items-center gap-3">
            <h1 class="text-2xl font-bold text-gray-900">{{ task.name }}</h1>
            <Badge :variant="'subtle'" :theme="getStatusTheme(task.status)" :label="task.status" />
            <Badge :variant="'outline'" :theme="getPriorityTheme(task.priority)" :label="task.priority + ' Priority'" />
          </div>
          <div class="flex items-center gap-2 mt-1">
            <p class="text-sm text-gray-500">Customer: <span class="font-semibold text-gray-700">{{ customerName }}</span></p>
            <span class="text-gray-300">|</span>
            <p class="text-sm text-gray-500">Code: <span class="font-mono font-semibold text-gray-700">{{ task.customer_code }}</span></p>
            <button v-if="isManager" @click="openCustomerSearch" class="text-blue-500 hover:text-blue-700 text-xs flex items-center gap-1 bg-blue-50 px-2 py-0.5 rounded transition" title="Change Customer">
              <LucideEdit class="w-3.5 h-3.5" /> Edit
            </button>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <Button v-if="isManager" variant="subtle" class="text-red-600 bg-red-50 hover:bg-red-100" @click="deleteTask">
          <template #prefix><LucideTrash2 class="w-4 h-4" /></template>
          Delete
        </Button>
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

      </div>
    </div>

    <!-- Main Content Area -->
    <div class="flex-1 overflow-hidden flex flex-col md:flex-row">
      <!-- Left side: Activity Logs / Tables -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6">
        <!-- Stat Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex flex-col justify-between">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-gray-500">Total Receivable</span>
              <button v-if="isManager" @click="openEditTaskModal" class="text-gray-400 hover:text-blue-500 transition" title="Edit Amount">
                <LucideEdit class="w-4 h-4" />
              </button>
            </div>
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
                <span class="px-2 py-0.5 rounded-full text-xs font-bold" :class="activeTab === 'calls' ? 'bg-white/20 text-white' : 'bg-blue-200 text-blue-800'">{{ task.call_history?.length || 0 }}</span>
              </button>

              <!-- Commitments Tab -->
              <button
                @click="activeTab = 'commitments'"
                class="px-4 py-2 rounded-full text-sm font-semibold transition-all duration-300 flex items-center gap-2 border whitespace-nowrap"
                :class="activeTab === 'commitments' ? 'bg-red-500 text-white border-red-600 shadow-md' : 'bg-red-50 text-red-600 border-red-100 hover:bg-red-100 hover:border-red-200 hover:text-red-700'"
              >
                <LucideCalendarClock class="w-4 h-4" /> Payment Commitments
                <span class="px-2 py-0.5 rounded-full text-xs font-bold" :class="activeTab === 'commitments' ? 'bg-white/20 text-white' : 'bg-red-200 text-red-800'">{{ task.payment_commitments?.length || 0 }}</span>
              </button>

              <!-- Receipts Tab -->
              <button
                @click="activeTab = 'receipts'"
                class="px-4 py-2 rounded-full text-sm font-semibold transition-all duration-300 flex items-center gap-2 border whitespace-nowrap"
                :class="activeTab === 'receipts' ? 'bg-orange-500 text-white border-orange-600 shadow-md' : 'bg-orange-50 text-orange-600 border-orange-100 hover:bg-orange-100 hover:border-orange-200 hover:text-orange-700'"
              >
                <LucideReceipt class="w-4 h-4" /> Receipts & Payments
                <span class="px-2 py-0.5 rounded-full text-xs font-bold" :class="activeTab === 'receipts' ? 'bg-white/20 text-white' : 'bg-orange-200 text-orange-800'">{{ task.payment_receipts?.length || 0 }}</span>
              </button>
            </div>
          </div>

          <!-- Tab Contents -->
          <div class="p-6 flex-1 overflow-y-auto">
            <!-- TAB 0: ACTIVITY LOG -->
            <div v-if="activeTab === 'activity'" class="h-full">
              <TaskActivityPanel doctype="Payment Collection Task" :docname="task.name" />
            </div>

            <!-- TAB 1: CALL HISTORY -->
            <div v-if="activeTab === 'calls'" class="space-y-4">
              <div class="flex items-center justify-between mb-2">
                <h3 class="font-bold text-gray-800">Call Logs</h3>
                  <Button variant="solid" class="bg-gray-900 text-white hover:bg-gray-800" @click="openLogCallModal">
                    <template #prefix><LucidePhone class="w-4 h-4" /></template>
                    Log Call
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
                            @click="openReceiptModalForCommitment(c.name, c.promised_amount, false)"
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
                          <button
                            @click="openReceiptModalForCommitment(c.name, c.promised_amount, true)"
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
                      <th class="py-3 px-4 font-semibold text-gray-600 text-right">Actions</th>
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
                      <td class="py-3 px-4 text-right">
                        <button @click="openEditReceiptModal(r)" class="text-blue-600 hover:bg-blue-50 p-1.5 rounded transition" title="Edit Receipt">
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

      <!-- Right side: Sidebar Info -->
      <div 
        class="border-t md:border-t-0 md:border-l border-gray-200 bg-white transition-all duration-300 flex flex-col relative h-full"
        :class="isRightSidebarCollapsed ? 'w-12' : 'w-full md:w-80'"
      >
        <div v-show="!isRightSidebarCollapsed" class="p-6 space-y-6 overflow-y-auto flex-1">
        <!-- Task Details -->
        <div class="space-y-4">
          <h4 class="text-xs font-bold uppercase tracking-wider text-gray-400">Assignment Details</h4>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between items-center">
              <span class="text-gray-500">Purpose:</span>
              <select
                v-if="isManager"
                v-model="task.purpose_type"
                @change="updateField('purpose_type', task.purpose_type)"
                class="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 font-medium text-gray-900 bg-gray-50 max-w-[150px]"
              >
                <option value="Software Payment">Software Payment</option>
                <option value="AMC">AMC</option>
                <option value="New Feature">New Feature</option>
                <option value="Customization">Customization</option>
                <option value="Support">Support</option>
                <option value="Other">Other</option>
              </select>
              <span v-else class="font-medium text-gray-900">{{ task.purpose_type }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-500">Assignee:</span>
              <select
                v-if="isManager"
                v-model="task.assigned_to"
                @change="updateField('assigned_to', task.assigned_to)"
                class="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 font-medium text-gray-900 bg-gray-50"
              >
                <option v-for="(name, email) in userMap" :key="email" :value="email">{{ name }}</option>
              </select>
              <span v-else class="font-medium text-gray-900">{{ getUserFullName(task.assigned_to) }}</span>
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
          </div>
          <div class="space-y-3 text-sm">
            <div>
              <span class="text-gray-500 block text-xs mb-1">Primary Contact:</span>
              <input
                v-if="isManager"
                v-model="task.contact_person"
                @blur="updateField('contact_person', task.contact_person)"
                type="text"
                class="w-full border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 font-semibold text-gray-900 bg-gray-50"
              />
              <span v-else class="font-semibold text-gray-900">{{ task.contact_person }}</span>
            </div>

            <div>
              <span class="text-gray-500 block text-xs mb-1">Primary Mobile:</span>
              <div v-if="isManager" class="flex gap-2">
                <input
                  v-model="task.mobile_number"
                  @blur="updateField('mobile_number', task.mobile_number)"
                  type="text"
                  class="flex-1 border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 font-bold text-blue-600 bg-gray-50"
                />
              </div>
              <a v-else :href="'tel:' + task.mobile_number" class="inline-flex items-center gap-1 font-bold text-blue-600 hover:underline">
                <LucidePhone class="w-3.5 h-3.5 text-blue-500" />
                {{ task.mobile_number }}
              </a>
            </div>

            <div v-if="task.alternate_mobile || isManager">
              <span class="text-gray-500 block text-xs mb-1">Alternate Mobile:</span>
              <div v-if="isManager" class="flex gap-2">
                <input
                  v-model="task.alternate_mobile"
                  @blur="updateField('alternate_mobile', task.alternate_mobile)"
                  type="text"
                  placeholder="Optional"
                  class="flex-1 border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 font-medium text-gray-700 bg-gray-50"
                />
              </div>
              <a v-else-if="task.alternate_mobile" :href="'tel:' + task.alternate_mobile" class="inline-flex items-center gap-1 font-medium text-gray-700 hover:underline">
                <LucidePhone class="w-3.5 h-3.5 text-gray-400" />
                {{ task.alternate_mobile }}
              </a>
            </div>
          </div>
        </div>

        <!-- Description -->
        <div class="space-y-4 border-t pt-4">
          <h4 class="text-xs font-bold uppercase tracking-wider text-gray-400">Purpose Description</h4>
          <textarea
            v-if="isManager"
            v-model="task.task_description"
            @blur="updateField('task_description', task.task_description)"
            rows="4"
            class="w-full text-sm text-gray-600 leading-relaxed bg-gray-50 p-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
          ></textarea>
          <p v-else class="text-sm text-gray-600 whitespace-pre-wrap leading-relaxed bg-gray-50 p-3 rounded-lg border border-gray-100">
            {{ task.task_description }}
          </p>
        </div>
        </div>
        
        <!-- Toggle Button Container -->
        <div class="border-t border-gray-200 p-3 mt-auto bg-gray-50/50 flex" :class="isRightSidebarCollapsed ? 'justify-center' : 'justify-start'">
          <button 
            @click="isRightSidebarCollapsed = !isRightSidebarCollapsed"
            class="flex items-center gap-2 p-1.5 hover:bg-gray-200 rounded text-gray-600 text-sm font-medium transition-colors"
            title="Toggle Sidebar"
          >
            <LucideChevronRight v-if="!isRightSidebarCollapsed" class="w-4 h-4" />
            <LucideChevronLeft v-else class="w-4 h-4" />
            <span v-if="!isRightSidebarCollapsed">Collapse</span>
          </button>
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
                :class="{'bg-gray-100 text-gray-400': receiptForm.payment_mode === 'Cash'}"
                :disabled="receiptForm.payment_mode === 'Cash'"
              />
            </div>

            <!-- Next Follow-up Date -->
            <div class="col-span-1 md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">Next Follow-up Date (Optional)</label>
              <input
                v-model="receiptForm.next_follow_up_date"
                type="date"
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
              <select v-model="editReceiptForm.payment_mode" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none bg-white">
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
import LucidePhoneCall from "~icons/lucide/phone-call";
import LucidePlus from "~icons/lucide/plus";
import LucideCheck from "~icons/lucide/check";
import LucidePhone from "~icons/lucide/phone";
import LucideCalendar from "~icons/lucide/calendar";
import LucideTrash2 from "~icons/lucide/trash-2";
import LucideEdit from "~icons/lucide/edit";
import CustomerSearchPopup from "@/components/CustomerSearchPopup.vue";
import TaskActivityPanel from "@/components/TaskActivityPanel.vue";
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
const activeTab = ref("receipts");
const isRightSidebarCollapsed = ref(false);

// Cache maps
const userMap = ref<Record<string, string>>({});

// Modals
const showCustomerSearch = ref(false);
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
async function deleteTask() {
  if (!confirm("Are you sure you want to permanently delete this Payment Collection Task?")) return;
  try {
    await call("frappe.client.delete", { doctype: "Payment Collection Task", name: props.taskId });
    router.push({ name: 'PaymentCollectionTaskList' });
  } catch (err: any) {
    console.error("Failed to delete task:", err);
    alert(err.message || "Failed to delete task.");
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
    
    if (task.value && task.value.status === 'Open') {
      task.value.status = 'In Progress';
    }
    
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

function openReceiptModalForCommitment(commitmentId: string, promisedAmount: number, isPartial: boolean) {
  receiptForm.value = {
    amount_received: isPartial ? '' : promisedAmount,
    payment_mode: "Bank Transfer",
    transaction_reference: "",
    remarks: "",
    next_follow_up_date: "",
    commitment_row_id: commitmentId,
    commitment_status: isPartial ? "Partially Paid" : "Received"
  };
  isReceiptAmountReadonly.value = !isPartial;
  receiptModalOpen.value = true;
}

async function saveReceipt() {
  if (!receiptForm.value.amount_received || Number(receiptForm.value.amount_received) <= 0) {
    alert("Please enter a valid amount received.");
    return;
  }
  if (Number(receiptForm.value.amount_received) > task.value.outstanding_amount) {
    alert("Amount received cannot be greater than the outstanding payable amount.");
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
    remarks: receipt.remarks || ""
  };
  editReceiptModalOpen.value = true;
}

async function saveEditReceipt() {
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
  } catch (error) {
    console.error("Failed to update receipt details:", error);
    alert("Failed to update receipt details. Check console for error.");
  } finally {
    isReceiptEditing.value = false;
  }
}
</script>
