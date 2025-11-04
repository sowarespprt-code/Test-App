<template>
  <div class="flex w-[382px] flex-col border-l gap-4">
    <!-- Ticket ID -->
    <div class="flex items-center justify-between border-b px-5 py-3">
      <span class="cursor-copy text-lg font-semibold">Ticket details</span>
    </div>
    <!-- user info and sla info -->
    <div class="flex flex-col gap-4 pt-0 px-5 py-3 border-b">
      <!-- user info -->
      <div class="flex gap-2">
        <Avatar
          size="2xl"
          :image="ticket.data?.contact?.image"
          :label="ticket.data?.contact?.name || 'New Ticket'"
        />
        <div class="flex items-center justify-between">
          <Tooltip :text="ticket.data?.contact?.name || 'New Ticket'">
            <div class="w-[242px] truncate text-2xl font-medium">
              {{ ticket.data?.contact?.name || 'New Ticket' }}
            </div>
          </Tooltip>
          <div class="flex gap-1.5" v-if="ticket.data && !ticket.data.feedback_rating">
            <Tooltip :text="ticket.data.contact.email_id">
              <Button class="h-7 w-7" @click="emit('open')">
                <template #icon>
                  <EmailIcon class="h-4 w-4" />
                </template>
              </Button>
            </Tooltip>
          </div>
        </div>
      </div>

      <!-- Ticket Info -->
      <div
        class="flex items-center text-base leading-5"
        v-for="field in ticketBasicInfo"
        :key="field.label"
      >
        <span class="w-[126px] text-sm text-gray-600">{{ field.label }}</span>
        <span
          class="text-base text-gray-800 flex-1"
          :class="!field.value && 'text-ink-gray-4'"
        >
          {{ field.value || "—" }}
        </span>
      </div>

      <!-- sla info -->
      <div
        v-if="ticket.data"
        v-for="data in slaData"
        :key="data.label"
        class="flex items-center text-base"
      >
        <div class="w-[126px] text-gray-600 text-sm">{{ data.title }}</div>

        <div class="break-words text-base text-gray-800">
          <Tooltip :text="dayjs(data.value).long()">
            <Badge :label="data.label" :theme="data.theme" variant="subtle" />
          </Tooltip>
        </div>
      </div>
    </div>
    <!-- feedback component -->
    <TicketFeedback
      v-if="ticket.data?.feedback_rating"
      class="border-b text-base text-gray-600"
      :ticket="ticket.data"
    />
    <div class="flex flex-col gap-4 pt-0 px-5 py-3">
      <div
        class="flex items-center text-base leading-5"
        v-for="field in ticketAdditionalInfo"
        :key="field.label"
      >
        <span class="w-[126px] text-sm text-gray-600">{{ field.label }}</span>
        <span
          class="text-base text-gray-800 flex-1"
          :class="!field.value && 'text-ink-gray-4'"
        >
          {{ field.value || "—" }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { dayjs } from "@/dayjs";
import { ITicket } from "@/pages/ticket/symbols";
import { Field } from "@/types";
import { formatTime } from "@/utils";
import { Avatar, Tooltip, call, Badge, Button } from "frappe-ui";
import { computed, inject, ref, watch, onMounted, nextTick } from "vue";

const emit = defineEmits(["open"]);
const ticket = inject(ITicket);

console.log("🚀 [SIDEBAR] Component initialized");

// Store virtual field values
const virtualFields = ref({
  custom_customercode: "",
  custom_product: "",
  custom_customer_name: "",
  isLoading: false,
});

// Multi-strategy loading function
async function loadVirtualFields() {
  await nextTick();
  
  const ticketId = ticket.data?.name;
  
  console.log("📥 [SIDEBAR] loadVirtualFields called");
  console.log("📥 [SIDEBAR] Ticket ID:", ticketId);
  
  if (!ticketId) {
    console.warn("⚠️ [SIDEBAR] No ticket ID available");
    virtualFields.value.isLoading = false;
    return;
  }

  virtualFields.value.isLoading = true;

  // Strategy 1: Check latest ticket
  console.log("🔍 [SIDEBAR] Strategy 1: Checking latest_ticket_virtual");
  const latestStored = sessionStorage.getItem('latest_ticket_virtual');
  
  if (latestStored) {
    try {
      const parsed = JSON.parse(latestStored);
      console.log("🔍 [SIDEBAR] Parsed:", parsed);
      
      if (parsed.ticketId == ticketId) {
        console.log("✅ [SIDEBAR] MATCH! Using latest_ticket_virtual");
        virtualFields.value.custom_customercode = parsed.custom_customercode || "";
        virtualFields.value.custom_product = parsed.custom_product || "";
        virtualFields.value.custom_customer_name = parsed.custom_customer_name || "";
        virtualFields.value.isLoading = false;
        
        sessionStorage.removeItem('latest_ticket_virtual');
        return;
      }
    } catch (error) {
      console.error("❌ [SIDEBAR] Parse error:", error);
    }
  }

  // Strategy 2: Check ticket-specific storage
  console.log("🔍 [SIDEBAR] Strategy 2: Checking ticket_virtual_" + ticketId);
  const storageKey = `ticket_virtual_${ticketId}`;
  const storedData = sessionStorage.getItem(storageKey);
  
  if (storedData) {
    try {
      const parsed = JSON.parse(storedData);
      console.log("✅ [SIDEBAR] Found stored data:", parsed);
      
      virtualFields.value.custom_customercode = parsed.custom_customercode || "";
      virtualFields.value.custom_product = parsed.custom_product || "";
      virtualFields.value.custom_customer_name = parsed.custom_customer_name || "";
      virtualFields.value.isLoading = false;
      return;
    } catch (error) {
      console.error("❌ [SIDEBAR] Parse error:", error);
    }
  }

  // Strategy 3: Fetch from customer
  console.log("🔍 [SIDEBAR] Strategy 3: Fetching from HD Customer");
  const customerName = ticket.data?.custom_customer_name;
  
  if (!customerName) {
    console.warn("⚠️ [SIDEBAR] No customer name");
    virtualFields.value.isLoading = false;
    return;
  }

  try {
    console.log("📡 [SIDEBAR] Fetching customer:", customerName);
    
    const result = await call("frappe.client.get_value", {
      doctype: "HD Customer",
      filters: { name: customerName },
      fieldname: ["custom_customercode", "custom_productname"]
    });

    console.log("✅ [SIDEBAR] API result:", result);
    
    if (result?.message) {
      virtualFields.value.custom_customercode = result.message.custom_customercode || "";
      virtualFields.value.custom_product = result.message.custom_productname || "";
    } else if (result) {
      virtualFields.value.custom_customercode = result.custom_customercode || "";
      virtualFields.value.custom_product = result.custom_productname || "";
    }
    
    virtualFields.value.custom_customer_name = customerName;
    
    // Cache result
    sessionStorage.setItem(storageKey, JSON.stringify({
      ticketId,
      custom_customercode: virtualFields.value.custom_customercode,
      custom_product: virtualFields.value.custom_product,
      custom_customer_name: virtualFields.value.custom_customer_name,
      timestamp: Date.now()
    }));
    
  } catch (error) {
    console.error("❌ [SIDEBAR] Fetch error:", error);
  } finally {
    virtualFields.value.isLoading = false;
  }
}

onMounted(async () => {
  console.log("🎬 [SIDEBAR] onMounted");
  await nextTick();
  setTimeout(() => loadVirtualFields(), 100);
});

watch(() => ticket.data?.name, async (newId, oldId) => {
  console.log("👀 [SIDEBAR] Ticket ID changed:", oldId, "->", newId);
  if (newId && newId !== oldId) {
    await nextTick();
    loadVirtualFields();
  }
}, { immediate: true });

watch(() => ticket.data, async (newData) => {
  if (newData?.name && !virtualFields.value.custom_customercode) {
    await nextTick();
    loadVirtualFields();
  }
}, { deep: true, immediate: true });

const slaData = computed(() => {
  if (!ticket.data) return [];
  
  const firstResponse = firstResponseData();
  const resolution = resolutionData();
  return [
    {
      title: "First Response",
      value: ticket.data.first_responded_on || ticket.data.response_by,
      label: firstResponse.label,
      theme: firstResponse.color,
    },
    {
      title: "Resolution",
      value: ticket.data.resolution_date || ticket.data.resolution_by,
      label: resolution.label,
      theme: resolution.color,
    },
  ];
});

function firstResponseData() {
  if (!ticket.data) return { label: "—", color: "gray" };
  
  if (!ticket.data.first_responded_on && dayjs().isBefore(dayjs(ticket.data.response_by))) {
    return {
      label: `Due in ${formatTime(dayjs(ticket.data.response_by).diff(dayjs(), "s"))}`,
      color: "orange",
    };
  } else if (dayjs(ticket.data.first_responded_on).isBefore(dayjs(ticket.data.response_by))) {
    return {
      label: `Fulfilled in ${formatTime(dayjs(ticket.data.first_responded_on).diff(dayjs(ticket.data.creation), "s"))}`,
      color: "green",
    };
  }
  return { label: "Failed", color: "red" };
}

function resolutionData() {
  if (!ticket.data) return { label: "—", color: "gray" };
  
  if (!ticket.data.resolution_date && dayjs().isBefore(ticket.data.resolution_by)) {
    return {
      label: `Due in ${formatTime(dayjs(ticket.data.resolution_by).diff(dayjs(), "s"))}`,
      color: "orange",
    };
  } else if (ticket.data.agreement_status === "Fulfilled") {
    return {
      label: `Fulfilled in ${formatTime(dayjs(ticket.data.resolution_time, "s"))}`,
      color: "green",
    };
  }
  return { label: "Failed", color: "red" };
}

const ticketBasicInfo = computed(() => {
  if (!ticket.data) {
    return [
      { label: "Ticket ID", value: "New Ticket" },
      { label: "Status", value: "Draft", bold: true },
    ];
  }
  
  return [
    { label: "Ticket ID", value: ticket.data.name },
    { label: "Status", value: ticket.data.status, bold: true },
  ];
});

const ticketAdditionalInfo = computed(() => {
  console.log("🔄 [SIDEBAR] Computing additionalInfo");
  
  if (!ticket.data) return [];

  const fields = [
    { label: "Subject", value: ticket.data.subject },
    { label: "Team", value: ticket.data.agent_group || "—" },
    { label: "Priority", value: ticket.data.priority },
  ];
  
  const templateFields = ticket.data?.template?.fields || [];
  
  const template_custom_fields = templateFields
    .filter((field: Field) =>
      !field.hide_from_customer &&
      !["subject", "team", "priority", "custom_customercode", "custom_product", "custom_customer_name"].includes(field.fieldname)
    )
    .map((field: Field) => ({
      label: field.label,
      value: ticket.data[field.fieldname],
    }));

  const virtualFieldsDisplay = [];
  
  if (templateFields.some((f: Field) => f.fieldname === "custom_customer_name")) {
    virtualFieldsDisplay.push({
      label: "Customer Name",
      value: virtualFields.value.custom_customer_name || ticket.data.custom_customer_name || "—",
    });
  }
  
  if (templateFields.some((f: Field) => f.fieldname === "custom_customercode")) {
    virtualFieldsDisplay.push({
      label: "Customer Code",
      value: virtualFields.value.isLoading ? "Loading..." : (virtualFields.value.custom_customercode || "—"),
    });
  }
  
  if (templateFields.some((f: Field) => f.fieldname === "custom_product")) {
    virtualFieldsDisplay.push({
      label: "Product",
      value: virtualFields.value.isLoading ? "Loading..." : (virtualFields.value.custom_product || "—"),
    });
  }

  return [...fields, ...virtualFieldsDisplay, ...template_custom_fields];
});
</script>

<style scoped></style>