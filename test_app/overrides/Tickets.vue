<template>
  <div>
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs
          label="Tickets"
          :route-name="isCustomerPortal ? 'TicketsCustomer' : 'TicketsAgent'"
          :options="dropdownOptions"
          :dropdown-actions="viewActions"
          :current-view="currentView"
        />
      </template>
      <template #right-header>
        <RouterLink
          :to="{ name: isCustomerPortal ? 'TicketNew' : 'TicketAgentNew' }"
        >
          <Button label="Create" theme="gray" variant="solid">
            <template #prefix>
              <LucidePlus class="h-4 w-4" />
            </template>
          </Button>
        </RouterLink>
      </template>
    </LayoutHeader>

    <!-- Update notification banner -->
    <transition name="slide-down">
      <div
        v-if="showUpdateBanner"
        class="mx-4 mt-4 mb-2 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg flex items-center justify-between shadow-sm"
      >
        <div class="flex items-center gap-2">
          <FeatherIcon name="refresh-cw" class="h-4 w-4 text-blue-600 dark:text-blue-400 animate-spin" />
          <span class="text-sm font-medium text-blue-800 dark:text-blue-200">
            {{ updateMessage }}
          </span>
        </div>
        <button
          @click="dismissBanner"
          class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 transition-colors"
        >
          <FeatherIcon name="x" class="h-4 w-4" />
        </button>
      </div>
    </transition>

    <ListViewBuilder
      ref="listViewRef"
      :options="options"
      @empty-state-action="handleEmptyStateAction"
      @row-click="handleRowClick"
    />

    <ExportModal
      v-model="showExportModal"
      :rowCount="$refs.listViewRef?.list?.data?.total_count ?? 0"
      @update="handleExport"
    />

    <ViewModal
      v-if="viewDialog.show"
      v-model="viewDialog"
      @update="handleView"
    />
  </div>
</template>

<script setup lang="ts">
import { LayoutHeader, ListViewBuilder } from "@/components";
import {
  EditIcon,
  IndicatorIcon,
  PinIcon,
  TicketIcon,
  UnpinIcon,
} from "@/components/icons";
import ExportModal from "@/components/ticket/ExportModal.vue";
import ViewBreadcrumbs from "@/components/ViewBreadcrumbs.vue";
import ViewModal from "@/components/ViewModal.vue";
import { currentView, useView } from "@/composables/useView";
import { dayjs } from "@/dayjs";
import { useAuthStore } from "@/stores/auth";
import { globalStore } from "@/stores/globalStore";
import { useTicketStatusStore } from "@/stores/ticketStatus";
import { View } from "@/types";
import { getIcon, isCustomerPortal } from "@/utils";
import { Badge, FeatherIcon, toast, Tooltip, usePageMeta } from "frappe-ui";
import { computed, h, onMounted, onBeforeUnmount, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

const router = useRouter();
const route = useRoute();
const showUpdateBanner = ref(false);
const updateMessage = ref("");

const {
  getCurrentUserViews,
  createView,
  publicViews,
  pinnedViews,
  findView,
  updateView,
  deleteView,
} = useView("HD Ticket");

const { $dialog, $socket } = globalStore();
const { isManager } = useAuthStore();

const listViewRef = ref(null);
const showExportModal = ref(false);

const { getStatus } = useTicketStatusStore();

const listSelections = ref(new Set());
const selectBannerActions = [
  {
    label: "Export",
    icon: "download",
    onClick: (selections: Set<string>) => {
      listSelections.value = new Set(selections);
      showExportModal.value = true;
    },
  },
];

// Debounce and reload management
let reloadTimeout: ReturnType<typeof setTimeout> | null = null;
let bannerTimeout: ReturnType<typeof setTimeout> | null = null;

const debouncedReload = (message: string = "Tickets updated") => {
  if (reloadTimeout) {
    clearTimeout(reloadTimeout);
  }

  reloadTimeout = setTimeout(() => {
    if (listViewRef.value?.reload) {
      listViewRef.value.reload();
      updateMessage.value = message;
      showUpdateBanner.value = true;

      playNotificationSound();

      if (bannerTimeout) {
        clearTimeout(bannerTimeout);
      }
      bannerTimeout = setTimeout(() => {
        showUpdateBanner.value = false;
      }, 4000);
    }
  }, 500);
};

const dismissBanner = () => {
  showUpdateBanner.value = false;
  if (bannerTimeout) {
    clearTimeout(bannerTimeout);
  }
};

const playNotificationSound = () => {
  try {
    const audio = new Audio(
      "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZURE="
    );
    audio.volume = 0.3;
    audio.play().catch(() => {});
  } catch (error) {}
};

// Row class for SLA coloring
const getRowClass = (row: any) => {
  const status = getStatus(row.status);
  if (!status) return "hover:bg-gray-50 dark:hover:bg-gray-800/50";

  const statusColor = status?.color || status?.parsed_color;

  const colorMap = {
    red: "!bg-red-100 hover:!bg-red-200 dark:!bg-red-900/30 dark:hover:!bg-red-900/40",
    "light-red":
      "!bg-red-50 hover:!bg-red-100 dark:!bg-red-900/20 dark:hover:!bg-red-900/30",
    orange:
      "!bg-orange-100 hover:!bg-orange-200 dark:!bg-orange-900/30 dark:hover:!bg-orange-900/40",
    "light-orange":
      "!bg-orange-50 hover:!bg-orange-100 dark:!bg-orange-900/20 dark:hover:!bg-orange-900/30",
    yellow:
      "!bg-yellow-100 hover:!bg-yellow-200 dark:!bg-yellow-900/30 dark:hover:!bg-yellow-900/40",
    "light-yellow":
      "!bg-yellow-50 hover:!bg-yellow-100 dark:!bg-yellow-900/20 dark:hover:!bg-yellow-900/30",
    green:
      "!bg-green-100 hover:!bg-green-200 dark:!bg-green-900/30 dark:hover:!bg-green-900/40",
    "light-green":
      "!bg-green-50 hover:!bg-green-100 dark:!bg-green-900/20 dark:hover:!bg-green-900/30",
    blue: "!bg-blue-100 hover:!bg-blue-200 dark:!bg-blue-900/30 dark:hover:!bg-blue-900/40",
    "light-blue":
      "!bg-blue-50 hover:!bg-blue-100 dark:!bg-blue-900/20 dark:hover:!bg-blue-900/30",
    purple:
      "!bg-purple-100 hover:!bg-purple-200 dark:!bg-purple-900/30 dark:hover:!bg-purple-900/40",
    "light-purple":
      "!bg-purple-50 hover:!bg-purple-100 dark:!bg-purple-900/20 dark:hover:!bg-purple-900/30",
    pink:
      "!bg-pink-100 hover:!bg-pink-200 dark:!bg-pink-900/30 dark:hover:!bg-pink-900/40",
    "light-pink":
      "!bg-pink-50 hover:!bg-pink-100 dark:!bg-pink-900/20 dark:hover:!bg-pink-900/30",
    gray: "!bg-gray-100 hover:!bg-gray-200 dark:!bg-gray-700 dark:hover:!bg-gray-600",
    "light-gray":
      "!bg-gray-50 hover:!bg-gray-100 dark:!bg-gray-800 dark:hover:!bg-gray-700",
  };

  if (statusColor) {
    const colorKey = statusColor.toLowerCase().replace(/\s+/g, "-");
    if (colorMap[colorKey]) {
      return colorMap[colorKey];
    }
  }

  return "hover:bg-gray-50 dark:hover:bg-gray-800/50";
};

// List view options (same as new file, no behavioral change except rowClass)
const options = {
  doctype: "HD Ticket",
  columnConfig: {
    status: {
      custom: ({ item }) => {
        const status = getStatus(item);
        const label = isCustomerPortal.value
          ? status?.["label_customer"]
          : status?.["label_agent"];
        return h(
          "div",
          { class: "flex items-center space-x-2 justify-start w-full" },
          [
            h(IndicatorIcon, { class: status?.["parsed_color"] }),
            h("span", { class: "truncate flex-1" }, label),
          ]
        );
      },
    },
    agreement_status: {
      custom: ({ item }) => {
        return h(Badge, {
          label: item,
          theme: slaStatusColorMap[item],
          variant: "outline",
        });
      },
    },
    response_by: {
      custom: ({ row, item }) => handleResponseByField(row, item),
    },
    resolution_by: {
      custom: ({ row, item }) => handleResolutionByField(row, item),
    },
  },
  rowClass: getRowClass,
  isCustomerPortal: isCustomerPortal.value,
  selectable: true,
  showSelectBanner: true,
  selectBannerActions,
  emptyState: {
    title: "No Tickets Found",
    icon: h(TicketIcon, { class: "h-10 w-10" }),
  },
  rowRoute: {
    name: isCustomerPortal.value ? "TicketCustomer" : "TicketAgent",
    prop: "ticketId",
  },
  hideColumnSetting: false,
};

function handleResponseByField(row: any, item: string) {
  if (!row.first_responded_on && dayjs(item).isBefore(new Date())) {
    return h(Badge, {
      label: "Failed",
      theme: "red",
      variant: "outline",
    });
  }
  if (row.first_responded_on && dayjs(row.first_responded_on).isBefore(item)) {
    return h(Badge, {
      label: "Fulfilled",
      theme: "green",
      variant: "outline",
    });
  } else if (dayjs(row.first_responded_on).isAfter(item)) {
    return h(Badge, {
      label: "Failed",
      theme: "red",
      variant: "outline",
    });
  } else {
    return h(
      Tooltip,
      { text: dayjs(item).long() },
      () => dayjs.tz(item).fromNow()
    );
  }
}

function handleResolutionByField(row: any, item: string) {
  const status = getStatus(row.status) || {};
  if (status.category === "Paused") {
    return h(Badge, {
      label: "Paused",
      theme: "blue",
      variant: "outline",
    });
  } else if (row.resolution_date && dayjs(row.resolution_date).isBefore(item)) {
    return h(Badge, {
      label: "Fulfilled",
      theme: "green",
      variant: "outline",
    });
  } else if (dayjs(row.resolution_date).isAfter(item)) {
    return h(Badge, {
      label: "Failed",
      theme: "red",
      variant: "outline",
    });
  } else {
    return h(
      Tooltip,
      { text: dayjs(item).long() },
      () => dayjs.tz(item).fromNow()
    );
  }
}

// Export functionality (your new version kept)
async function handleExport({
  export_type,
  export_all,
}: {
  export_type: "CSV" | "Excel";
  export_all: boolean;
}) {
  const list = listViewRef.value?.list;
  if (!list) return;

  const fields = JSON.stringify(list.data.columns.map((f) => f.key));
  const order_by = list.params.order_by;

  let filters = { ...list.params.filters };
  let pageLength: number;

  if (export_all) {
    filters = JSON.stringify(filters);
    pageLength = list.data.total_count;
  } else {
    pageLength = listSelections.value.size;
    filters["name"] = ["in", Array.from(listSelections.value)];
    filters = JSON.stringify(filters);
  }

  window.location.href = `/api/method/frappe.desk.reportview.export_query?file_format_type=${export_type}&title=HD Ticket&doctype=HD Ticket&fields=${fields}&filters=${filters}&order_by=${order_by}&page_length=${pageLength}&start=0&view=Report&with_comment_count=1`;
  reset();
  showExportModal.value = false;
}

function reset(reload = false) {
  listViewRef.value?.unselectAll();
  listSelections.value?.clear();
  if (reload) listViewRef.value.reload();
}

const slaStatusColorMap = {
  Fulfilled: "green",
  Failed: "red",
  "Resolution Due": "orange",
  "First Response Due": "orange",
  Paused: "blue",
};

// ===== OLD VIEW / ADD COLUMN LOGIC (UNCHANGED) =====
let viewDialog = reactive({
  show: false,
  view: {
    label: "",
    icon: "",
    name: "",
  },
  mode: "create",
});

const dropdownOptions = computed(() => {
  const items = [
    {
      group: "Default Views",
      items: [
        {
          label: "List View",
          icon: "align-justify",
          onClick: () =>
            router.push({
              name: isCustomerPortal.value ? "TicketsCustomer" : "TicketsAgent"
            }),
        },
      ],
    },
  ];  //

  // Saved Views
  if (getCurrentUserViews.value?.length !== 0) {
    items.push({
      group: "Saved Views",
      items: parseViews(getCurrentUserViews.value),
    });
  }
  if (pinnedViews.value?.length !== 0) {
    items.push({
      group: "Private Views",
      items: parseViews(pinnedViews.value),
    });
  }
  if (publicViews.value?.length !== 0) {
    items.push({
      group: "Public Views",
      items: parseViews(publicViews.value),
    });
  }

  items.push({
    group: "Create View",
    hideLabel: true,
    items: [
      {
        label: "Create View",
        icon: "plus",
        onClick: () => {
          resetState();
          viewDialog.show = true;
        },
      },
    ],
  });

  return items;
});

let selectedView: View | null = null;

const viewActions = (view) => {
  const _view = findView(view.name).value;

  let actions = [
    {
      group: "Default Views",
      hideLabel: true,
      items: [
        {
          label: "Duplicate",
          icon: h(FeatherIcon, { name: "copy" }),
          onClick: () => {
            viewDialog.view.label = _view.label + " (New)";
            viewDialog.view.icon = _view.icon;
            viewDialog.view.name = _view.name;
            viewDialog.mode = "duplicate";
            selectedView = _view;
            viewDialog.show = true;
          },
        },
      ],
    },
  ];
  if (!_view.public || isManager) {
    actions[0].items.push({
      label: "Edit",
      icon: h(EditIcon, { class: "h-4 w-4" }),
      onClick: () => {
        viewDialog.view.label = _view.label;
        viewDialog.view.icon = _view.icon;
        viewDialog.view.name = _view.name;
        viewDialog.mode = "edit";
        viewDialog.show = true;
      },
    });
    if (!_view.public) {
      actions[0].items.push({
        label: _view?.pinned ? "Unpin View" : "Pin View",
        icon: h(_view?.pinned ? UnpinIcon : PinIcon, { class: "h-4 w-4" }),
        onClick: () => {
          const newView = {
            name: _view.name,
          };
          newView["pinned"] = !_view.pinned;
          updateView(newView);
        },
      });
    }
    if (isManager && !isCustomerPortal.value) {
      actions[0].items.push({
        label: _view?.public ? "Make Private" : "Make Public",
        icon: h(FeatherIcon, {
          name: _view?.public ? "lock" : "unlock",
          class: "h-4 w-4",
        }),
        onClick: () => {
          const newView = {
            name: _view.name,
            public: !_view.public,
          };

          if (_view.public) {
            $dialog({
              title: `Make ${_view.label} private?`,
              message:
                "This view is currently public. Changing it to private will hide it for all the users.",
              actions: [
                {
                  label: "Confirm",
                  variant: "solid",
                  onClick({ close }) {
                    close();
                    updateView(newView);
                  },
                },
              ],
            });
          } else {
            updateView(newView);
          }
        },
      });
    }
    actions.push({
      group: "Delete View",
      hideLabel: true,
      items: [
        {
          label: "Delete",
          icon: "trash-2",
          onClick: () => {
            $dialog({
              title: `Delete ${_view.label}?`,
              message: `Are you sure you want to delete this view?
              ${
                _view.public
                  ? "This view is public, and will be removed for all users."
                  : ""
              }`,
              actions: [
                {
                  label: "Confirm",
                  variant: "solid",
                  onClick({ close }) {
                    if (route.query.view === _view.name) {
                      router.push({
                        name: isCustomerPortal.value
                          ? "TicketsCustomer"
                          : "TicketAgent",
                      });
                    }
                    deleteView(_view.name);
                    handleSuccess("deleted");
                    close();
                  },
                },
              ],
            });
          },
        },
      ],
    });
  }

  return actions;
};

function parseViews(views: View[]) {
  return views?.map((view) => {
    return {
      ...view,
      onClick: () => {
        currentView.value = {
          label: view.label,
          icon: view.icon,
        };
        router.push({
          name: view.route_name,
          query: {
            view: view.name,
          },
        });
      },
    };
  });
}

function handleView(viewInfo, action) {
  let view: View;
  if (action === "update") {
    updateView(viewInfo);
    handleSuccess("updated");
    currentView.value = {
      label: viewInfo.label,
      icon: getIcon(viewInfo.icon),
    };
    return;
  } else if (action === "duplicate") {
    view = {
      ...selectedView,
      filters: JSON.stringify(selectedView.filters),
      columns: JSON.stringify(selectedView.columns),
      rows: JSON.stringify(selectedView.rows),
      label: viewInfo.label,
      icon: viewInfo.icon,
      public: false,
      pinned: false,
    };
  } else {
    view = {
      dt: "HD Ticket",
      type: "list",
      label: viewInfo.label ?? "List",
      icon: viewInfo.icon ?? "",
      route_name: router.currentRoute.value.name as string,
      order_by: listViewRef.value?.list?.params.order_by,
      filters: JSON.stringify(listViewRef.value?.list?.params.filters),
      columns: JSON.stringify(listViewRef.value?.list?.data.columns),
      rows: JSON.stringify(listViewRef.value?.list?.data?.rows),
      is_customer_portal: isCustomerPortal.value,
    };
  }

  // createView
  createView(view, (d) => {
    currentView.value = {
      label: d.label || "List",
      icon: getIcon(d.icon),
    };
    router.push({
      name: isCustomerPortal.value ? "TicketsCustomer" : "TicketsAgent",
      query: {
        view: d.name,
      },
    });

    handleSuccess();
  });
}

function handleSuccess(msg = "created") {
  toast.success(`View ${msg}`);
  resetState();
}
function resetState() {
  viewDialog.show = false;
  viewDialog.view.label = "";
  viewDialog.view.icon = "";
  viewDialog.view.name = "";
  viewDialog.mode = null;
  selectedView = null;
}

// Event handlers
function handleEmptyStateAction() {
  router.push({
    name: isCustomerPortal.value ? "TicketNew" : "TicketAgentNew",
  });
}

function handleRowClick(row) {
  router.push({
    name: isCustomerPortal.value ? "TicketCustomer" : "TicketAgent",
    params: { ticketId: row },
  });
}

// Cleanup intervals
let pollInterval: ReturnType<typeof setInterval> | null = null;

// Setup real-time updates
onMounted(() => {
  if (!route.query.view) {
    currentView.value = {
      label: "List",
      icon: "lucide:align-justify",
    };
  }
  
  console.log("✅ Setting up real-time ticket updates...");
  
  // Socket event listeners
  $socket.on("helpdesk:new-ticket", (data) => {
    console.log("🎫 New ticket created:", data);
    debouncedReload("🎫 New ticket created");
  });
  
  $socket.on("ticket_updated", (data) => {
    console.log("✏️ Ticket updated:", data);
    debouncedReload("✏️ Ticket updated");
  });
  
  $socket.on("helpdesk:ticket-update", (data) => {
    console.log("🔄 Ticket status changed:", data);
    debouncedReload("🔄 Ticket status changed");
  });
  
  $socket.on("helpdesk:ticket-assignee-update", (data) => {
    console.log("👤 Ticket assigned:", data);
    debouncedReload("👤 Ticket assignment changed");
  });
  
  $socket.on("ticket_deleted", (data) => {
    console.log("🗑️ Ticket deleted:", data);
    debouncedReload("🗑️ Ticket deleted");
  });
  
  $socket.on("ticket_assigned", (data) => {
    console.log("✅ Ticket assigned:", data);
    debouncedReload("✅ Ticket assigned");
  });
  
  // Fallback polling every 30 seconds
  pollInterval = setInterval(() => {
    if (listViewRef.value?.reload) {
      console.log("🔄 Polling for updates...");
      listViewRef.value.reload();
    }
  }, 30000);
  
  console.log("✅ Real-time updates initialized");
});

// Cleanup on unmount
onBeforeUnmount(() => {
  console.log("🧹 Cleaning up real-time updates...");
  
  // Clear timeouts
  if (reloadTimeout) clearTimeout(reloadTimeout);
  if (bannerTimeout) clearTimeout(bannerTimeout);
  
  // Clear polling interval
  if (pollInterval) clearInterval(pollInterval);
  
  // Remove socket listeners
  $socket.off("helpdesk:new-ticket");
  $socket.off("ticket_updated");
  $socket.off("helpdesk:ticket-update");
  $socket.off("helpdesk:ticket-assignee-update");
  $socket.off("ticket_deleted");
  $socket.off("ticket_assigned");
  
  console.log("✅ Cleanup complete");
});

usePageMeta(() => {
  return {
    title: "Tickets",
  };
});
</script>

<style scoped>
/* Fix z-index issue for column dropdowns */
:deep(.column-settings-dropdown),
:deep(.frappe-dropdown-menu),
:deep([data-testid="column-settings"]) {
  z-index: 9999 !important;
}

/* Ensure ListViewBuilder column settings appear above other dropdowns */
:deep(.list-view-builder .dropdown-menu),
:deep(.list-view-builder [role="menu"]) {
  z-index: 10000 !important;
}
</style>
