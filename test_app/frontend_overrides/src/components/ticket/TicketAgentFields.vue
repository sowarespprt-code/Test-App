<template>
  <div class="flex flex-1 flex-col overflow-hidden overflow-y-auto border-b">
    <TicketField
      v-for="field in fields"
      :key="field.fieldname"
      :field="field"
      :value="getFieldValue(field.fieldname)"
      @change="(data) => update(data.fieldname, data.value)"
    />
  </div>
</template>

<script setup lang="ts">
import { Field, FieldValue, TicketSymbol } from "@/types";
import { toast, call } from "frappe-ui";
import { computed, ref, watch, onMounted, nextTick, onActivated, inject } from "vue";
import TicketField from "../TicketField.vue";

const emit = defineEmits(["update"]);

// ✅ CHANGE: Use TicketSymbol instead of ITicket
const ticket = inject(TicketSymbol);

console.log("[AGENT FIELDS] 🚀 Component mounted");
console.log("[AGENT FIELDS] 🚀 Injected ticket:", ticket);
console.log("[AGENT FIELDS] 🚀 Ticket value:", ticket.value);
console.log("[AGENT FIELDS] 🚀 Ticket data:", ticket.value?.data);

const virtualFieldsCache = ref({
  custom_customercode: "",
  custom_product: "",
  loaded: false,
});

const refreshKey = ref(0);

async function loadVirtualFields(ticketId: string) {
  console.log("[AGENT FIELDS] 📥 loadVirtualFields called for ticket:", ticketId);
  
  if (!ticketId) {
    console.warn("[AGENT FIELDS] ⚠️ No ticket ID provided");
    return;
  }

  virtualFieldsCache.value.loaded = false;

  // Strategy 1: Check latest_ticket_virtual
  console.log("[AGENT FIELDS] 🔍 Strategy 1: Checking latest_ticket_virtual");
  const latestStored = sessionStorage.getItem('latest_ticket_virtual');
  console.log("[AGENT FIELDS] 🔍 latest_ticket_virtual:", latestStored);
  
  if (latestStored) {
    try {
      const data = JSON.parse(latestStored);
      console.log("[AGENT FIELDS] 🔍 Found latest_ticket_virtual:", data);
      
      if (String(data.ticketId) === String(ticketId)) {
        console.log("[AGENT FIELDS] ✅ MATCH! Using latest_ticket_virtual");
        virtualFieldsCache.value.custom_customercode = data.custom_customercode || "";
        virtualFieldsCache.value.custom_product = data.custom_product || "";
        virtualFieldsCache.value.loaded = true;
        refreshKey.value++;
        
        console.log("[AGENT FIELDS] ✅ Cache updated:", virtualFieldsCache.value);
        sessionStorage.removeItem('latest_ticket_virtual');
        return;
      }
    } catch (e) {
      console.error("[AGENT FIELDS] ❌ Parse error for latest_ticket_virtual:", e);
    }
  }

  // Strategy 2: Check ticket-specific storage
  console.log("[AGENT FIELDS] 🔍 Strategy 2: Checking ticket_virtual_" + ticketId);
  const storageKey = `ticket_virtual_${ticketId}`;
  const stored = sessionStorage.getItem(storageKey);
  console.log("[AGENT FIELDS] 🔍 Stored data:", stored);

  if (stored) {
    try {
      const data = JSON.parse(stored);
      console.log("[AGENT FIELDS] ✅ Found stored data:", data);
      
      virtualFieldsCache.value.custom_customercode = data.custom_customercode || "";
      virtualFieldsCache.value.custom_product = data.custom_product || "";
      virtualFieldsCache.value.loaded = true;
      refreshKey.value++;
      
      console.log("[AGENT FIELDS] ✅ Cache updated from storage:", virtualFieldsCache.value);
      return;
    } catch (e) {
      console.error("[AGENT FIELDS] ❌ Parse error:", e);
    }
  }

  // Strategy 3: Fetch from customer
  console.log("[AGENT FIELDS] 🔍 Strategy 3: Fetching from HD Customer");
  const customerName = ticket.value?.data?.custom_customer_name;
  console.log("[AGENT FIELDS] 🔍 Customer name:", customerName);
  
  if (customerName) {
    try {
      console.log("[AGENT FIELDS] 📡 Fetching from HD Customer:", customerName);
      
      const result = await call("frappe.client.get_value", {
        doctype: "HD Customer",
        filters: { name: customerName },
        fieldname: ["custom_customercode", "custom_productname"],
      });

      console.log("[AGENT FIELDS] ✅ Fetch result:", result);

      if (result?.message) {
        virtualFieldsCache.value.custom_customercode = result.message.custom_customercode || "";
        virtualFieldsCache.value.custom_product = result.message.custom_productname || "";
      } else if (result) {
        virtualFieldsCache.value.custom_customercode = result.custom_customercode || "";
        virtualFieldsCache.value.custom_product = result.custom_productname || "";
      }
      
      virtualFieldsCache.value.loaded = true;
      refreshKey.value++;
      console.log("[AGENT FIELDS] ✅ Cache updated from API:", virtualFieldsCache.value);
      
      sessionStorage.setItem(storageKey, JSON.stringify({
        ticketId,
        custom_customercode: virtualFieldsCache.value.custom_customercode,
        custom_product: virtualFieldsCache.value.custom_product,
        timestamp: Date.now()
      }));
      
    } catch (e) {
      console.error("[AGENT FIELDS] ❌ Fetch error:", e);
    }
  }
}

onMounted(async () => {
  console.log("[AGENT FIELDS] 🎬 onMounted triggered");
  await nextTick();
  
  const ticketId = ticket.value?.data?.name || ticket.value?.name;
  console.log("[AGENT FIELDS] 🎬 Ticket ID on mount:", ticketId);
  
  if (ticketId) {
    loadVirtualFields(ticketId);
    
    setTimeout(() => {
      console.log("[AGENT FIELDS] ⏰ Delayed load triggered");
      if (!virtualFieldsCache.value.loaded) {
        console.log("[AGENT FIELDS] ⏰ Cache not loaded yet, retrying...");
        loadVirtualFields(ticketId);
      }
    }, 300);
  } else {
    console.warn("[AGENT FIELDS] 🎬 No ticket ID found!");
  }
});

onActivated(() => {
  console.log("[AGENT FIELDS] 🔄 Component activated (keep-alive)");
  const ticketId = ticket.value?.data?.name || ticket.value?.name;
  if (ticketId) {
    loadVirtualFields(ticketId);
  }
});

watch(
  () => ticket.value?.data?.name || ticket.value?.name,
  async (newTicketId, oldTicketId) => {
    console.log("[AGENT FIELDS] 👀 Ticket ID watcher triggered");
    console.log("[AGENT FIELDS] 👀 Old:", oldTicketId, "New:", newTicketId);
    
    if (newTicketId && newTicketId !== oldTicketId) {
      virtualFieldsCache.value.loaded = false;
      await nextTick();
      loadVirtualFields(newTicketId);
    }
  },
  { immediate: true }
);

watch(
  () => ticket.value?.data,
  async (newTicket) => {
    console.log("[AGENT FIELDS] 👀 Ticket object watcher triggered");
    console.log("[AGENT FIELDS] 👀 New ticket data:", newTicket);
    
    if (newTicket?.name && !virtualFieldsCache.value.loaded) {
      console.log("[AGENT FIELDS] 👀 Ticket loaded but no cache yet");
      await nextTick();
      loadVirtualFields(newTicket.name);
    }
  },
  { deep: true, immediate: true }
);

const fields = computed(() => {
  const _ = refreshKey.value;
  const fieldsList = ticket.value?.data?.fields || [];
  console.log("[AGENT FIELDS] 📋 Computing fields, count:", fieldsList.length);
  return fieldsList;
});

function getFieldValue(fieldname: string) {
  const _ = refreshKey.value;
  
  if (fieldname === "custom_customercode") {
    const value = virtualFieldsCache.value.custom_customercode || "";
    console.log("[AGENT FIELDS] 🔄 Getting customer code:", value);
    return value;
  }
  
  if (fieldname === "custom_product") {
    const value = virtualFieldsCache.value.custom_product || "";
    console.log("[AGENT FIELDS] 🔄 Getting product:", value);
    return value;
  }
  
  const value = ticket.value?.data[fieldname];
  console.log("[AGENT FIELDS] 🔄 Getting field", fieldname + ":", value);
  return value;
}

function update(field: Field["fieldname"], value: FieldValue, event = null) {
  console.log("[AGENT FIELDS] 💾 Update called for:", field, "with value:", value);
  
  if (field === "subject" && value === "") {
    toast.error("Subject is required");
    if (event?.target) {
      event.target.value = ticket.value?.data.subject;
    }
    return;
  }
  
  emit("update", { field, value });
}
</script>

<style scoped>
:deep(.form-control input:not([type="checkbox"])),
:deep(.form-control select),
:deep(.form-control textarea),
:deep(.form-control button) {
  border-color: transparent;
  background: white;
}

:deep(.form-control textarea) {
  field-sizing: content;
}

:deep(.form-control button) {
  gap: 0;
}

:deep(.form-control [type="checkbox"]) {
  margin-left: 9px;
  cursor: pointer;
}

:deep(.form-control button > div) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.form-control button svg) {
  color: white;
  width: 0;
}
</style>
