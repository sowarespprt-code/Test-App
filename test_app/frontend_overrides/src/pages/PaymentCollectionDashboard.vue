<template>
  <div class="flex flex-col h-full bg-gray-50">
    <!-- Header -->
    <div class="border-b px-6 py-4 flex items-center justify-between bg-white shadow-sm">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Payment Collection Dashboard</h1>
        <p class="text-sm text-gray-500 mt-1">Real-time overview of collections, outstanding dues, and agent follow-up schedules.</p>
      </div>
      <Button variant="solid" @click="fetchMetrics" :loading="isLoading">
        <template #prefix>
          <LucideRefreshCw class="w-4 h-4" :class="isLoading ? 'animate-spin' : ''" />
        </template>
        Refresh Dashboard
      </Button>
    </div>

    <!-- Content Area -->
    <div v-if="metrics" class="flex-1 overflow-y-auto p-6 space-y-6">
      <!-- KPI Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
        <!-- 1. Total Outstanding -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex flex-col justify-between">
          <div class="flex justify-between items-center text-gray-400">
            <span class="text-xs font-bold uppercase tracking-wider">Total Outstanding</span>
            <LucideAlertCircle class="w-5 h-5 text-red-500" />
          </div>
          <span class="text-xl font-extrabold text-red-600 mt-2">{{ formatCurrency(metrics.total_outstanding_amount) }}</span>
          <span class="text-xs text-gray-500 mt-1">Active balance due</span>
        </div>

        <!-- 2. Collected This Month -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex flex-col justify-between">
          <div class="flex justify-between items-center text-gray-400">
            <span class="text-xs font-bold uppercase tracking-wider">Collected (Month)</span>
            <LucideTrendingUp class="w-5 h-5 text-green-500" />
          </div>
          <span class="text-xl font-bold text-green-600 mt-2">{{ formatCurrency(metrics.total_collected_this_month) }}</span>
          <span class="text-xs text-gray-500 mt-1">Received this month</span>
        </div>

        <!-- 3. Open Tasks -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex flex-col justify-between">
          <div class="flex justify-between items-center text-gray-400">
            <span class="text-xs font-bold uppercase tracking-wider">Open Tasks</span>
            <LucideFileText class="w-5 h-5 text-blue-500" />
          </div>
          <span class="text-2xl font-bold text-blue-600 mt-2">{{ metrics.open_collection_tasks }}</span>
          <span class="text-xs text-gray-500 mt-1">Tasks requiring action</span>
        </div>

        <!-- 4. Overdue Follow-ups -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex flex-col justify-between" :class="metrics.overdue_follow_ups > 0 ? 'bg-orange-50/20 border-orange-100' : ''">
          <div class="flex justify-between items-center text-gray-400">
            <span class="text-xs font-bold uppercase tracking-wider text-orange-700">Overdue Follow-ups</span>
            <LucideCalendar class="w-5 h-5 text-orange-500" />
          </div>
          <span class="text-2xl font-bold text-orange-600 mt-2">{{ metrics.overdue_follow_ups }}</span>
          <span class="text-xs text-gray-500 mt-1">Pending callback date</span>
        </div>

        <!-- 5. Failed Commitments -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex flex-col justify-between" :class="metrics.failed_commitments > 0 ? 'bg-red-50/20 border-red-100' : ''">
          <div class="flex justify-between items-center text-gray-400">
            <span class="text-xs font-bold uppercase tracking-wider text-red-700">Failed Promises</span>
            <LucideXCircle class="w-5 h-5 text-red-500" />
          </div>
          <span class="text-2xl font-bold text-red-600 mt-2">{{ metrics.failed_commitments }}</span>
          <span class="text-xs text-gray-500 mt-1">Unpaid promised dates</span>
        </div>
      </div>

      <!-- Reminder Alerts Section -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div class="border-b bg-gray-50 px-6 py-4">
          <h2 class="font-bold text-gray-800 flex items-center gap-2">
            <LucideClock class="w-5 h-5 text-blue-500" />
            Reminders & Follow-up Lists
          </h2>
        </div>
        
        <div class="p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Overdue Reminders -->
          <div class="space-y-4">
            <div class="flex items-center justify-between border-b pb-2">
              <span class="font-bold text-red-600 text-sm flex items-center gap-1.5">
                <span class="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse"></span>
                Overdue Follow-ups ({{ metrics.overdue_reminders?.length || 0 }})
              </span>
            </div>
            
            <div v-if="metrics.overdue_reminders && metrics.overdue_reminders.length" class="space-y-3 max-h-[350px] overflow-y-auto pr-1">
              <div
                v-for="task in metrics.overdue_reminders"
                :key="task.name"
                class="p-3 border border-red-100 rounded-lg hover:bg-gray-50 cursor-pointer transition bg-white"
                @click="viewTask(task.name)"
              >
                <div class="flex justify-between text-xs font-bold text-blue-600 mb-1">
                  <span>{{ task.name }}</span>
                  <span class="text-red-600">Overdue: {{ formatDate(task.next_follow_up_date) }}</span>
                </div>
                <div class="text-sm font-semibold text-gray-800 truncate">{{ task.customer_name_display }}</div>
                <div class="flex justify-between items-center mt-2 text-xs text-gray-500">
                  <span>Assignee: {{ task.assigned_to_name }}</span>
                  <span class="font-bold text-red-600">Due: {{ formatCurrency(task.outstanding_amount) }}</span>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-8 text-xs text-gray-400 bg-gray-50 rounded-lg">
              No overdue follow-ups!
            </div>
          </div>

          <!-- Today's Reminders -->
          <div class="space-y-4">
            <div class="flex items-center justify-between border-b pb-2">
              <span class="font-bold text-orange-600 text-sm flex items-center gap-1.5">
                <span class="w-2.5 h-2.5 rounded-full bg-orange-500"></span>
                Today's Reminders ({{ metrics.daily_reminders?.length || 0 }})
              </span>
            </div>
            
            <div v-if="metrics.daily_reminders && metrics.daily_reminders.length" class="space-y-3 max-h-[350px] overflow-y-auto pr-1">
              <div
                v-for="task in metrics.daily_reminders"
                :key="task.name"
                class="p-3 border border-orange-100 rounded-lg hover:bg-gray-50 cursor-pointer transition bg-white"
                @click="viewTask(task.name)"
              >
                <div class="flex justify-between text-xs font-bold text-blue-600 mb-1">
                  <span>{{ task.name }}</span>
                  <span class="text-orange-600">Today</span>
                </div>
                <div class="text-sm font-semibold text-gray-800 truncate">{{ task.customer_name_display }}</div>
                <div class="flex justify-between items-center mt-2 text-xs text-gray-500">
                  <span>Assignee: {{ task.assigned_to_name }}</span>
                  <span class="font-bold text-orange-600">Due: {{ formatCurrency(task.outstanding_amount) }}</span>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-8 text-xs text-gray-400 bg-gray-50 rounded-lg">
              No follow-ups scheduled for today.
            </div>
          </div>

          <!-- Upcoming Follow-ups -->
          <div class="space-y-4">
            <div class="flex items-center justify-between border-b pb-2">
              <span class="font-bold text-blue-600 text-sm flex items-center gap-1.5">
                <span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
                Upcoming Follow-ups ({{ metrics.upcoming_follow_ups?.length || 0 }})
              </span>
            </div>
            
            <div v-if="metrics.upcoming_follow_ups && metrics.upcoming_follow_ups.length" class="space-y-3 max-h-[350px] overflow-y-auto pr-1">
              <div
                v-for="task in metrics.upcoming_follow_ups"
                :key="task.name"
                class="p-3 border border-blue-100 rounded-lg hover:bg-gray-50 cursor-pointer transition bg-white"
                @click="viewTask(task.name)"
              >
                <div class="flex justify-between text-xs font-bold text-blue-600 mb-1">
                  <span>{{ task.name }}</span>
                  <span class="text-gray-500">Next: {{ formatDate(task.next_follow_up_date) }}</span>
                </div>
                <div class="text-sm font-semibold text-gray-800 truncate">{{ task.customer_name_display }}</div>
                <div class="flex justify-between items-center mt-2 text-xs text-gray-500">
                  <span>Assignee: {{ task.assigned_to_name }}</span>
                  <span class="font-bold text-gray-700">Due: {{ formatCurrency(task.outstanding_amount) }}</span>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-8 text-xs text-gray-400 bg-gray-50 rounded-lg">
              No upcoming follow-ups scheduled.
            </div>
          </div>
        </div>
      </div>

      <!-- Analysis Tables (Staff performance & Customer Outstanding) -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Staff Performance -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div class="border-b bg-gray-50 px-6 py-4">
            <h2 class="font-bold text-gray-800 flex items-center gap-2">
              <LucideTrendingUp class="w-5 h-5 text-green-500" />
              Staff-wise Collection Performance
            </h2>
          </div>
          <div class="p-6">
            <div v-if="metrics.staff_performance && metrics.staff_performance.length" class="overflow-x-auto">
              <table class="w-full text-left text-sm border-collapse">
                <thead>
                  <tr class="bg-gray-50 border-b border-gray-200">
                    <th class="py-2.5 px-4 font-semibold text-gray-600">Staff Member</th>
                    <th class="py-2.5 px-4 font-semibold text-gray-600 text-right">Total Collected</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                  <tr v-for="staff in metrics.staff_performance" :key="staff.staff">
                    <td class="py-3 px-4 text-gray-900 font-medium">{{ staff.staff_name || staff.staff }}</td>
                    <td class="py-3 px-4 text-right font-bold text-green-600">{{ formatCurrency(staff.collected) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="text-center py-10 text-gray-400 text-sm">
              No collection receipts recorded yet.
            </div>
          </div>
        </div>

        <!-- Customer Outstanding Summary -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div class="border-b bg-gray-50 px-6 py-4">
            <h2 class="font-bold text-gray-800 flex items-center gap-2">
              <LucideAlertCircle class="w-5 h-5 text-red-500" />
              Customer-wise Outstanding Summary
            </h2>
          </div>
          <div class="p-6">
            <div v-if="metrics.customer_outstanding && metrics.customer_outstanding.length" class="overflow-x-auto">
              <table class="w-full text-left text-sm border-collapse">
                <thead>
                  <tr class="bg-gray-50 border-b border-gray-200">
                    <th class="py-2.5 px-4 font-semibold text-gray-600">Customer</th>
                    <th class="py-2.5 px-4 font-semibold text-gray-600 text-right">Outstanding Balance</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                  <tr v-for="cust in metrics.customer_outstanding" :key="cust.customer_name">
                    <td class="py-3 px-4 text-gray-900 font-medium">{{ cust.customer_display || cust.customer_name }}</td>
                    <td class="py-3 px-4 text-right font-extrabold text-red-600">{{ formatCurrency(cust.outstanding) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="text-center py-10 text-gray-400 text-sm">
              No outstanding customer balances found!
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Spinner -->
    <div v-else class="flex-1 flex items-center justify-center">
      <div class="flex flex-col items-center gap-3">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
        <p class="text-sm text-gray-500">Generating collection reports & dashboard metrics...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { call, Button } from "frappe-ui";
import LucideRefreshCw from "~icons/lucide/refresh-cw";
import LucideAlertCircle from "~icons/lucide/alert-circle";
import LucideTrendingUp from "~icons/lucide/trending-up";
import LucideFileText from "~icons/lucide/file-text";
import LucideCalendar from "~icons/lucide/calendar";
import LucideXCircle from "~icons/lucide/x-circle";
import LucideClock from "~icons/lucide/clock";

const router = useRouter();
const metrics = ref<any>(null);
const isLoading = ref(false);

onMounted(async () => {
  await fetchMetrics();
});

async function fetchMetrics() {
  isLoading.value = true;
  try {
    const data = await call("test_app.api.get_payment_dashboard_metrics");
    metrics.value = data;
  } catch (err) {
    console.error("Failed to load dashboard metrics:", err);
  } finally {
    isLoading.value = false;
  }
}

function viewTask(taskId: string) {
  router.push({ name: "PaymentCollectionTaskDetail", params: { taskId } });
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
</script>
