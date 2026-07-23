<template>
  <div class="flex flex-col h-full bg-white">
    <!-- Header -->
    <div class="border-b px-5 py-4 flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Follow-up Reminders</h1>
        <p class="text-sm text-gray-500 mt-1">Pending tasks ordered by next follow-up date. Today's follow-ups are highlighted.</p>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="border-b px-5 py-3 bg-gray-50 flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center gap-3 flex-1 max-w-4xl">
        <!-- Search -->
        <div class="relative flex-1">
          <input
            v-model="searchQuery"
            @keyup.enter="applyFilter"
            type="text"
            placeholder="Search by customer name or task number..."
            class="w-full px-3 py-2 pr-8 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
          />
          <LucideSearch class="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        </div>

        <!-- Date Filter -->
        <div class="flex items-center gap-2">
          <input
            v-model="fromDate"
            type="date"
            class="px-2 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          />
          <span class="text-sm text-gray-500">to</span>
          <input
            v-model="toDate"
            type="date"
            class="px-2 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          />
          <button
            @click="applyFilter"
            class="px-3 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
          >
            Filter
          </button>
        </div>
      </div>

      <div class="flex items-center gap-2 text-sm text-gray-500">
        <span>Found {{ filteredTasks.length }} tasks</span>
      </div>
    </div>

    <!-- Task List -->
    <div class="flex-1 overflow-auto">
      <!-- Loading state -->
      <div v-if="isLoading" class="flex items-center justify-center h-64">
        <div class="flex flex-col items-center gap-3">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <div class="text-sm text-gray-500">Loading reminders...</div>
        </div>
      </div>

      <!-- Content -->
      <template v-else>
        <div v-if="filteredTasks.length" class="overflow-x-auto">
          <table class="w-full divide-y divide-gray-200">
            <thead class="bg-gray-50 sticky top-0 z-10">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 tracking-wider">Next Follow-up</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Task Number</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Customer Name</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Assigned To</th>
                <th class="px-6 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Outstanding</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Status</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 tracking-wider">Priority</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="task in filteredTasks"
                :key="task.name"
                :class="getRowClass(task.next_follow_up_date)"
                class="transition-colors duration-150"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm font-bold">
                  {{ formatDate(task.next_follow_up_date) || '—' }}
                  <span v-if="isToday(task.next_follow_up_date)" class="ml-2 text-[10px] uppercase bg-red-100 text-red-700 px-1.5 py-0.5 rounded-full font-bold">Today</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span 
                    class="text-sm font-semibold hover:underline cursor-pointer"
                    :class="isToday(task.next_follow_up_date) ? 'text-orange-900' : 'text-blue-600'"
                    @click="openTaskDetail(task.name)"
                  >
                    {{ task.name }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">
                    {{ task.customer_display_name || task.customer }}
                  </div>
                  <div class="text-xs font-mono text-gray-500">
                    {{ task.customer_code || '—' }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-600">{{ task.assigned_to_display || task.assigned_to }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right font-bold text-sm" :class="task.outstanding_amount > 0 ? 'text-red-600' : 'text-green-600'">
                  {{ formatCurrency(task.outstanding_amount) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <Badge :variant="'subtle'" :theme="getStatusTheme(task.status)" :label="task.status" />
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-flex items-center text-xs font-medium" :class="getPriorityColor(task.priority)">
                    <span class="w-1.5 h-1.5 rounded-full mr-1.5" :class="getPriorityBg(task.priority)"></span>
                    {{ task.priority || 'Medium' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Empty state -->
        <div v-else class="flex flex-col items-center justify-center py-20 px-4">
          <div class="bg-gray-100 p-4 rounded-full text-gray-400 mb-4">
            <LucideFileText class="h-10 w-10" />
          </div>
          <h3 class="text-lg font-medium text-gray-900 mb-1">No pending reminders</h3>
          <p class="text-sm text-gray-500 max-w-sm text-center">
            You are all caught up!
          </p>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from "vue";
import { useRouter } from "vue-router";
import { call, Badge } from "frappe-ui";
import { useAuthStore } from "@/stores/auth";
import LucideSearch from "~icons/lucide/search";
import LucideFileText from "~icons/lucide/file-text";

const router = useRouter();
const tasks = ref<any[]>([]);
const isLoading = ref(false);
const searchQuery = ref("");
const appliedSearchQuery = ref("");
const fromDate = ref("");
const toDate = ref("");
const appliedFromDate = ref("");
const appliedToDate = ref("");
const todayStr = new Date().toISOString().split('T')[0];

onMounted(async () => {
  await fetchTasks();
  
  // Auto refresh every 5 minutes
  refreshInterval = window.setInterval(() => {
    fetchTasks();
  }, 300000);
});

onUnmounted(() => {
  if (refreshInterval) window.clearInterval(refreshInterval);
});

let refreshInterval: number | null = null;
async function fetchTasks() {
  isLoading.value = true;
  try {
    const authStore = useAuthStore();
    
    // Frappe requires an array of filters if we want to use operators
    let filters: any[] = [
      ["Payment Collection Task", "next_follow_up_date", "is", "set"],
      ["Payment Collection Task", "status", "not in", ["Completed", "Cancelled"]]
    ];

    if (!authStore.isManager) {
      filters.push(["Payment Collection Task", "assigned_to", "=", authStore.userId]);
    }

    const list = await call("frappe.client.get_list", {
      doctype: "Payment Collection Task",
      filters: filters,
      fields: [
        "name",
        "customer",
        "customer_code",
        "purpose_type",
        "payment_amount",
        "outstanding_amount",
        "status",
        "priority",
        "next_follow_up_date",
        "assigned_to"
      ],
      order_by: "next_follow_up_date desc",
      limit_page_length: 500
    });

    // Resolve HD Customer names in batch
    const uniqueCustomers = [...new Set(list.map((task: any) => task.customer).filter(Boolean))];
    let customerMap: Record<string, string> = {};

    if (uniqueCustomers.length > 0) {
      const customers = await call("frappe.client.get_list", {
        doctype: "HD Customer",
        filters: [["name", "in", uniqueCustomers]],
        fields: ["name", "customer_name"],
        limit_page_length: 500
      });
      customers.forEach((c: any) => {
        customerMap[c.name] = c.customer_name;
      });
    }

    // Resolve User full names in batch
    const uniqueUsers = [...new Set(list.map((task: any) => task.assigned_to).filter(Boolean))];
    let userMap: Record<string, string> = {};
    if (uniqueUsers.length > 0) {
      const users = await call("frappe.client.get_list", {
        doctype: "User",
        filters: [["name", "in", uniqueUsers]],
        fields: ["name", "full_name"],
        limit_page_length: 500
      });
      users.forEach((u: any) => {
        userMap[u.name] = u.full_name;
      });
    }

    tasks.value = list.map((task: any) => ({
      ...task,
      customer_display_name: customerMap[task.customer] || task.customer,
      assigned_to_display: userMap[task.assigned_to] || task.assigned_to
    }));
  } catch (err) {
    console.error("Failed to load reminders:", err);
  } finally {
    isLoading.value = false;
  }
}

const filteredTasks = computed(() => {
  let filtered = tasks.value.filter((task) => {
    let matchesSearch = task.name.toLowerCase().includes(appliedSearchQuery.value.toLowerCase()) ||
           task.customer.toLowerCase().includes(appliedSearchQuery.value.toLowerCase()) ||
           (task.customer_code && task.customer_code.toLowerCase().includes(appliedSearchQuery.value.toLowerCase())) ||
           (task.customer_display_name &&
            task.customer_display_name.toLowerCase().includes(appliedSearchQuery.value.toLowerCase()));
            
    // Date filter
    let matchesDate = true;
    if (appliedFromDate.value && task.next_follow_up_date) {
      if (task.next_follow_up_date < appliedFromDate.value) {
        matchesDate = false;
      }
    }
    if (appliedToDate.value && task.next_follow_up_date) {
      if (task.next_follow_up_date > appliedToDate.value) {
        matchesDate = false;
      }
    }
    
    return matchesSearch && matchesDate;
  });

  return filtered.sort((a, b) => {
    const timeA = a.next_follow_up_date ? new Date(a.next_follow_up_date).getTime() : 0;
    const timeB = b.next_follow_up_date ? new Date(b.next_follow_up_date).getTime() : 0;
    return timeB - timeA;
  });
});

function applyFilter() {
  appliedFromDate.value = fromDate.value;
  appliedToDate.value = toDate.value;
  appliedSearchQuery.value = searchQuery.value;
}

function isToday(dateStr: string) {
  if (!dateStr) return false;
  return dateStr === todayStr;
}

function getRowClass(dateStr: string) {
  if (!dateStr) return "hover:bg-gray-50/50";
  // Highlight if today
  if (dateStr === todayStr) {
    return "animate-row-blink";
  }
  // Highlight if overdue (past)
  if (dateStr < todayStr) {
    return "bg-red-50 hover:bg-red-100";
  }
  return "hover:bg-gray-50/50";
}

function openTaskDetail(taskName: string) {
  router.push({ name: 'CallManagementTaskDetail', params: { taskId: taskName } });
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

function getPriorityColor(priority: string) {
  switch (priority) {
    case "Urgent":
      return "text-red-700 font-semibold";
    case "High":
      return "text-orange-700";
    case "Medium":
      return "text-blue-700";
    case "Low":
      return "text-gray-700";
    default:
      return "text-blue-700";
  }
}

function getPriorityBg(priority: string) {
  switch (priority) {
    case "Urgent":
      return "bg-red-500";
    case "High":
      return "bg-orange-500";
    case "Medium":
      return "bg-blue-500";
    case "Low":
      return "bg-gray-400";
    default:
      return "bg-blue-500";
  }
}
</script>

<style>
@keyframes row-blink {
  0%, 100% { background-color: #ffedd5; } /* orange-100 */
  50% { background-color: #fdba74; } /* orange-300 */
}
.animate-row-blink {
  animation: row-blink 1.2s ease-in-out infinite;
}
</style>
