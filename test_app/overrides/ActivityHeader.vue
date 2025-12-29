<template>
  <div
    class="md:mx-10 md:my-4 flex items-center justify-between text-lg font-medium mx-6 mb-4 !mt-8"
  >
    <!-- LEFT: labels + times -->
    <div class="flex items-center text-xl font-semibold text-gray-800 gap-4">
      <span>{{ title }}</span>
      <div
        v-if="title === 'Activity'"
        class="flex items-center gap-6 text-xs text-gray-500 mb-1"
      >
        <span v-if="startTimeDisplay">
          <span class="font-semibold">Start:</span> {{ formatTime(startTimeDisplay) }}
        </span>
        <span v-if="endTimeDisplay">
          <span class="font-semibold">End:</span> {{ formatTime(endTimeDisplay) }}
        </span>
      </div>
    </div>

    <!-- RIGHT: buttons -->
    <div class="flex items-center gap-2" style="position: relative; z-index: 10;">
      <!-- Start / Close Ticket button -->
      <button
        v-if="showStartClose && title === 'Activity'"
        :disabled="isUpdating"
        :class="[
          'px-3 py-1.5 text-sm font-medium rounded-lg transition-colors duration-200',
          'focus:outline-none focus:ring-2 focus:ring-offset-1',
          'touch-manipulation',
          isUpdating 
            ? 'bg-gray-400 text-white cursor-not-allowed' 
            : isTicketStarted 
              ? 'bg-red-500 hover:bg-red-600 text-white focus:ring-red-500' 
              : 'bg-green-500 hover:bg-green-600 text-white focus:ring-green-500'
        ]"
        style="pointer-events: auto; -webkit-tap-highlight-color: transparent; user-select: none;"
        @click.stop="handleButtonClick"
      >
        {{ isUpdating 
          ? (isTicketStarted ? 'Closing...' : 'Starting...') 
          : (isTicketStarted ? 'Close Ticket' : 'Start Ticket') }}
      </button>

      <Button
        v-if="title == 'Emails'"
        variant="solid"
        @click="communicationAreaRef?.toggleEmailBox() ?? toggleEmailBox()"
      >
        <template #prefix>
          <FeatherIcon name="plus" class="h-4 w-4" />
        </template>
        <span>New Email</span>
      </Button>

      <Button
        v-else-if="title == 'Comments'"
        variant="solid"
        @click="communicationAreaRef?.toggleCommentBox() ?? toggleCommentBox()"
      >
        <template #prefix>
          <FeatherIcon name="plus" class="h-4 w-4" />
        </template>
        <span>New Comment</span>
      </Button>

      <Dropdown v-else-if="title == 'Calls'" :options="callActions" @click.stop>
        <template #default="{ open }">
          <Button variant="solid" class="flex items-center gap-1">
            <template #prefix>
              <FeatherIcon name="plus" class="h-4 w-4" />
            </template>
            <span>New</span>
            <template #suffix>
              <FeatherIcon
                :name="open ? 'chevron-up' : 'chevron-down'"
                class="h-4 w-4"
              />
            </template>
          </Button>
        </template>
      </Dropdown>

      <Dropdown v-else :options="defaultActions" @click.stop>
        <template #default="{ open }">
          <Button variant="solid" class="flex items-center gap-1">
            <template #prefix>
              <FeatherIcon name="plus" class="h-4 w-4" />
            </template>
            <span>New</span>
            <template #suffix>
              <FeatherIcon
                :name="open ? 'chevron-up' : 'chevron-down'"
                class="h-4 w-4"
              />
            </template>
          </Button>
        </template>
      </Dropdown>
    </div>
  </div>

  <CallLogModal
    v-model="showCallLogModal"
    :ticketId="ticketId"
    @after-insert="refreshTicket"
  />

  <!-- ✅ Close Ticket Modal -->
  <TicketCommentModal
    v-model="showCloseModal"
    :ticket-name="props.ticketName"
    @success="onCloseWithComment"
  />
</template>

<script setup lang="ts">
import { CommentIcon, EmailIcon, PhoneIcon } from "@/components/icons";
import CallLogModal from "@/pages/call-logs/CallLogModal.vue";
import TicketCommentModal from "@/components/ticket/TicketCommentModal.vue";
import { useTelephonyStore } from "@/stores/telephony";
import { toggleCommentBox, toggleEmailBox } from "@/pages/ticket/modalStates";
import { Dropdown, Button, call } from "frappe-ui";
import { storeToRefs } from "pinia";
import { ActivitiesSymbol } from "@/types";
import { computed, h, inject, ref, Ref, watch, onMounted } from "vue";

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  ticketName: {
    type: String,
    required: false,
    default: "",
  },
  ticketStatus: {
    type: String,
    required: false,
    default: "",
  },
  customStartTime: {
    type: String,
    required: false,
    default: "",
  },
  customEndTime: {
    type: String,
    required: false,
    default: "",
  }
});

const communicationAreaRef: Ref = inject("communicationArea");
const makeCall = inject<() => void>("makeCall");
const refreshTicket = inject<() => void>("refreshTicket");
const showCallLogModal = ref(false);
const showCloseModal = ref(false);
const { isCallingEnabled } = storeToRefs(useTelephonyStore());
const ticketId = inject<string>("ticketId");

const isTicketStarted = ref(false);
const startedStatuses = ["In Progress", "Replied", "Resolved"];
const isUpdating = ref(false);

const fetchedStartTime = ref("");
const fetchedEndTime = ref("");

const fetchTicketTimes = async () => {
  if (!props.ticketName) return;
  
  try {
    const result = await call("frappe.client.get_value", {
      doctype: "HD Ticket",
      filters: { name: props.ticketName },
      fieldname: ["custom_start_time", "custom_end_time"]
    });
    
    if (result) {
      fetchedStartTime.value = result.custom_start_time || "";
      fetchedEndTime.value = result.custom_end_time || "";
    }
  } catch (e) {
    console.error("Failed to fetch times:", e);
  }
};

onMounted(async () => {
  syncButtonWithStatus();
  await fetchTicketTimes();
});

watch(
  () => props.ticketName,
  async (newName) => {
    if (newName) {
      await fetchTicketTimes();
    }
  }
);

watch(
  () => props.ticketStatus,
  () => {
    syncButtonWithStatus();
  }
);

const handleButtonClick = async () => {
  if (isUpdating.value) return;
  
  if (isTicketStarted.value) {
    showCloseModal.value = true;
  } else {
    await handleStartTicket();
  }
};

const defaultActions = computed(() => {
  let actions = [
    {
      icon: h(EmailIcon, { class: "h-4 w-4" }),
      label: "Email",
      onClick: () =>
        communicationAreaRef?.value?.toggleEmailBox() ?? toggleEmailBox(),
    },
    {
      icon: h(CommentIcon, { class: "h-4 w-4" }),
      label: "Comment",
      onClick: () =>
        communicationAreaRef?.value?.toggleCommentBox() ?? toggleCommentBox(),
    },
  ];
  if (isCallingEnabled.value) {
    actions.push(...callActions.value);
  }
  return actions;
});

const callActions = computed(() => [
  {
    icon: h(PhoneIcon, { class: "h-4 w-4" }),
    label: "Make a Call",
    onClick: () => makeCall && makeCall(),
  },
  {
    icon: "edit-3",
    label: "Log a Call",
    onClick: () => {
      showCallLogModal.value = true;
    },
  },
]);

const syncButtonWithStatus = () => {
  const status = props.ticketStatus;
  isTicketStarted.value = startedStatuses.includes(status);
};

const startTimeDisplay = computed(() => fetchedStartTime.value || props.customStartTime || '');
const endTimeDisplay = computed(() => fetchedEndTime.value || props.customEndTime || '');

const nowFrappeFormat = () => {
  const d = new Date();
  const pad = (n: number) => n.toString().padStart(2, "0");
  return (
    d.getFullYear() +
    "-" + pad(d.getMonth() + 1) +
    "-" + pad(d.getDate()) +
    " " + pad(d.getHours()) +
    ":" + pad(d.getMinutes()) +
    ":" + pad(d.getSeconds())
  );
};

const formatTime = (timeStr: string) => {
  if (!timeStr) return '';
  const date = new Date(timeStr);
  if (window.innerWidth < 768) {
    return date.toLocaleTimeString('en-IN', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  }
  return date.toLocaleString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  });
};

const showStartClose = computed(() => {
  const status = props.ticketStatus;
  const hiddenStatuses = ["Closed", "Resolved", ""];
  return !hiddenStatuses.includes(status);
});

const handleStartTicket = async () => {
  if (!props.ticketName || isUpdating.value) return;
  
  isUpdating.value = true;
  try {
    const currentTime = nowFrappeFormat();
    
    await call("frappe.client.set_value", {
      doctype: "HD Ticket",
      name: props.ticketName,
      fieldname: "status",
      value: "In Progress",
    });
    
    await call("frappe.client.set_value", {
      doctype: "HD Ticket",
      name: props.ticketName,
      fieldname: "custom_start_time",
      value: currentTime,
    });
    
    isTicketStarted.value = true;
    await fetchTicketTimes();
    window.location.reload();
  } catch (e) {
    console.error("Start failed:", e);
    alert("Failed to start ticket");
  } finally {
    isUpdating.value = false;
  }
};

const onCloseWithComment = async (commentText: string) => {
  console.log('💬 Closing with comment:', commentText);
  
  if (!props.ticketName || isUpdating.value) return;
  
  isUpdating.value = true;
  try {
    const currentTime = nowFrappeFormat();
    
    await call("frappe.client.set_value", {
      doctype: "HD Ticket",
      name: props.ticketName,
      fieldname: "status",
      value: "Closed",
    });
    
    await call("frappe.client.set_value", {
      doctype: "HD Ticket",
      name: props.ticketName,
      fieldname: "custom_end_time",
      value: currentTime,
    });
    
    isTicketStarted.value = false;
    await fetchTicketTimes();
    
    console.log('✅ Ticket closed with comment');
    window.location.reload();
  } catch (e) {
    console.error("Close failed:", e);
    alert("Failed to close ticket");
  } finally {
    isUpdating.value = false;
  }
};
</script>
