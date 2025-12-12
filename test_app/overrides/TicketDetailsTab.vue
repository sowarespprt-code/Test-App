<template>
  <div
    class="h-full overflow-y-hidden flex flex-1 flex-col justify-between overflow-hidden max-h-full"
  >
    <div class="px-5 pb-4 flex flex-col">
      <!-- User avatar with buttons -->
      <TicketContact />
      <!-- Core Fields -->
      <div>
        <div
          v-for="(section, index) in coreFields"
          :key="index"
          :class="
            section.group ? 'flex gap-2 items-center w-full mb-3' : 'mb-3'
          "
        >
          <template v-for="field in section.fields">
            <Link
              v-if="field.visible"
              :key="field.fieldname"
              class="form-control-core"
              :class="section.group ? 'flex-1' : 'w-full'"
              :page-length="10"
              :label="field.label"
              :placeholder="field.placeholder"
              :doctype="field.doctype"
              :modelValue="field.value"
              :required="field.required"
              @update:model-value="
              (val:string) => handleFieldUpdate(field.fieldname, val,true)
            "
            />
          </template>
        </div>

        <!-- Assignee component -->
        <AssignTo />
      </div>
    </div>

    <!-- Additional Fields -->
    <div class="border-t flex flex-col flex-1 h-full pb-3 overflow-y-hidden">
      <!-- TODO: Hack of 80 % for now, will refactor -->
      <div class="overflow-y-scroll max-h-[80%]">
        <!-- Existing custom fields -->
        <template v-for="field in customFields">
          <TicketField
            v-if="field.visible"
            :key="field.fieldname"
            :field="field"
            :value="getFieldValueWithVirtual(field.fieldname)"
            @change="
              ({ fieldname, value }) => handleFieldUpdate(fieldname, value)
            "
          />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Link } from "@/components";
import { parseField } from "@/composables/formCustomisation";
import { useNotifyTicketUpdate } from "@/composables/realtime";
import { getMeta } from "@/stores/meta";
import {
  AssigneeSymbol,
  CustomizationSymbol,
  FieldValue,
  TicketSymbol,
} from "@/types";
import { computed, inject, ref, watch, onMounted, nextTick } from "vue";
import TicketField from "../TicketField.vue";
import AssignTo from "./AssignTo.vue";
import TicketContact from "./TicketContact.vue";
import { call } from "frappe-ui";

const ticket = inject(TicketSymbol);
const assignees = inject(AssigneeSymbol);
const customizations = inject(CustomizationSymbol);
const { getFields, getField } = getMeta("HD Ticket");
const { notifyTicketUpdate } = useNotifyTicketUpdate(ticket.value?.name);

// Virtual fields state (includes popup messages from localStorage)
const virtualFields = ref({
  custom_customercode: "",
  custom_product: "",
  custom_popup_messages: "", // ← Loaded from localStorage
});

// Fetch virtual fields from HD Customer and localStorage
async function loadVirtualFields() {
  const customerName = ticket?.value?.doc?.custom_customer_name;
  const ticketName = ticket?.value?.doc?.name;
  
  if (!customerName) {
    console.log("[DETAILS TAB] ⚠️ No customer name available");
    return;
  }

  console.log("[DETAILS TAB] 📥 Fetching virtual fields for:", customerName, "Ticket:", ticketName);

  try {
    // Fetch customer code and product name
    const result = await call("frappe.client.get_value", {
      doctype: "HD Customer",
      filters: { name: customerName },
      fieldname: ["custom_customercode", "custom_productname"],
    });

    console.log("[DETAILS TAB] ✅ Fetch result:", result);

    if (result?.message) {
      virtualFields.value.custom_customercode = result.message.custom_customercode || "";
      virtualFields.value.custom_product = result.message.custom_productname || "";
    } else if (result) {
      virtualFields.value.custom_customercode = result.custom_customercode || "";
      virtualFields.value.custom_product = result.custom_productname || "";
    }

    // ✅ CRITICAL: Load popup messages from localStorage
    if (ticketName) {
      const storageKey = `ticket_popup_${ticketName}`;
      const storedPopupMessages = localStorage.getItem(storageKey);
      
      if (storedPopupMessages) {
        virtualFields.value.custom_popup_messages = storedPopupMessages;
        console.log("[DETAILS TAB] ✅ Popup messages loaded from localStorage:", storedPopupMessages);
      } else {
        // Fallback: Try to fetch from Customer Alert if not in localStorage
        console.log("[DETAILS TAB] ⚠️ No popup messages in localStorage, trying Customer Alert...");
        await fetchCustomerAlerts(customerName);
      }
    }

    console.log("[DETAILS TAB] ✅ Virtual fields loaded:", virtualFields.value);
  } catch (error) {
    console.error("[DETAILS TAB] ❌ Error fetching virtual fields:", error);
  }
}

// Fallback: Fetch customer alerts if localStorage doesn't have the data
async function fetchCustomerAlerts(customerName: string) {
  try {
    const customerCode = virtualFields.value.custom_customercode;
    let result: any[] = [];
    
    // Try by customer_code first
    if (customerCode) {
      result = await call('frappe.client.get_list', {
        doctype: 'Customer Alert',
        filters: { customer_code: customerCode },
        fields: ['name', 'popupmessage', 'modified'],
        order_by: 'modified desc',
        limit: 10
      });
    }
    
    // Fallback to customer_name
    if (!result || result.length === 0) {
      result = await call('frappe.client.get_list', {
        doctype: 'Customer Alert',
        filters: { customer_name: customerName },
        fields: ['name', 'popupmessage', 'modified'],
        order_by: 'modified desc',
        limit: 10
      });
    }
    
    if (result && result.length > 0) {
      virtualFields.value.custom_popup_messages = result
        .map(a => a.popupmessage)
        .filter(msg => msg)
        .join('\n\n') || '';
      
      console.log("[DETAILS TAB] ✅ Popup messages fetched from Customer Alert:", virtualFields.value.custom_popup_messages);
    }
  } catch (error) {
    console.error('[DETAILS TAB] ❌ Error fetching customer alerts:', error);
  }
}

// Load on mount
onMounted(async () => {
  console.log("[DETAILS TAB] 🎬 Component mounted");
  await nextTick();
  loadVirtualFields();
});

// Watch for customer_name changes
watch(
  () => ticket?.value?.doc?.custom_customer_name,
  async (newCustomerName, oldCustomerName) => {
    console.log("[DETAILS TAB] 👀 Customer name changed:", oldCustomerName, "->", newCustomerName);
    if (newCustomerName && newCustomerName !== oldCustomerName) {
      await nextTick();
      loadVirtualFields();
    }
  },
  { immediate: true }
);

// Watch for ticket name changes (when ticket is created/loaded)
watch(
  () => ticket?.value?.doc?.name,
  async (newTicketName, oldTicketName) => {
    console.log("[DETAILS TAB] 🎫 Ticket name changed:", oldTicketName, "->", newTicketName);
    if (newTicketName && newTicketName !== oldTicketName) {
      await nextTick();
      loadVirtualFields();
    }
  },
  { immediate: true }
);

const coreFields = computed(() => {
  const fieldsMeta = getFields();
  if (!fieldsMeta || fieldsMeta.length === 0) {
    return [];
  }
  const _coreFields = [
    { group: true, fields: [getField("ticket_type"), getField("priority")] },
    { group: false, fields: [getField("customer")] },
    { group: true, fields: [getField("agent_group")] },
  ];

  _coreFields.forEach((section) => {
    section.fields = section.fields.map((f) => {
      f = parseField(f, ticket.value.doc);
      f["required"] = f.reqd;
      f = getFieldInFormat(f, f);
      f["visible"] = true;
      return f;
    });
  });
  return _coreFields;
});

const customFields = computed(() => {
  const fieldsMeta = getFields();
  if (!fieldsMeta || fieldsMeta.length === 0) {
    return [];
  }

  if (!customizations.value.data || customizations.value.loading) return [];
  let customFields = customizations.value.data?.custom_fields || [];
  const _coreFields = [
    "ticket_type",
    "priority",
    "customer",
    "agent_group",
    "subject",
    "status",
  ];
  customFields = customFields.filter((f) => !_coreFields.includes(f.fieldname));
  let _customFields = customFields.map((f) => {
    let fieldMeta = getField(f.fieldname);
    fieldMeta = parseField(fieldMeta, ticket.value.doc);
    fieldMeta["required"] = fieldMeta.reqd || f.required;
    return getFieldInFormat(f, fieldMeta);
  });
  return _customFields;
});

const isTicketCreated = computed(() => {
  return ticket.value?.doc?.name && !ticket.value.doc.__islocal;
});

function getFieldInFormat(fieldTemplate, fieldMeta) {
  // Virtual fields that should always be readonly
  const virtualReadonlyFields = [
    "custom_product",
    "custom_customercode", 
    "custom_popup_messages",
    "custom_popupmessage" // Support both naming conventions
  ];
  
  const isVirtualField = virtualReadonlyFields.includes(fieldTemplate.fieldname);
  const shouldBeReadonly = isVirtualField && isTicketCreated.value;

  return {
    label: fieldMeta?.label || fieldTemplate.fieldname,
    value: ticket.value.doc[fieldTemplate.fieldname],
    fieldtype: fieldMeta?.fieldtype,
    doctype: fieldMeta?.options || "",
    options: fieldMeta?.options || "",
    placeholder:
      fieldTemplate.placeholder ||
      `Enter ${fieldMeta?.label || fieldTemplate.fieldname}`,
    readonly: Boolean(fieldMeta.readonly) || shouldBeReadonly,
    disabled: Boolean(fieldMeta.readonly) || shouldBeReadonly,
    url_method: fieldTemplate.url_method || "",
    fieldname: fieldTemplate.fieldname,
    required: fieldTemplate.required || fieldMeta?.required || false,
    visible: fieldMeta.display_via_depends_on && !fieldMeta.hidden,
  };
}

// Return virtual field value from memory, not from database
function getFieldValueWithVirtual(fieldname: string) {
  // Support both naming conventions
  if (fieldname === "custom_popup_messages" || fieldname === "custom_popupmessage") {
    console.log("[DETAILS TAB] 📤 Returning popup messages:", virtualFields.value.custom_popup_messages);
    return virtualFields.value.custom_popup_messages;
  }
  if (fieldname === "custom_customercode") {
    return virtualFields.value.custom_customercode;
  }
  if (fieldname === "custom_product") {
    return virtualFields.value.custom_product;
  }
  return ticket.value.doc[fieldname];
}

function handleFieldUpdate(
  fieldname: string,
  value: FieldValue,
  isCoreFieldUpdated = false
) {
  // Prevent updates for virtual fields
  const virtualFields = [
    "custom_popup_messages", 
    "custom_popupmessage",
    "custom_product", 
    "custom_customercode"
  ];
  
  if (virtualFields.includes(fieldname)) {
    console.log(`[DETAILS TAB] ⛔ Skipping update for virtual field: ${fieldname}`);
    return;
  }

  if (ticket.value.doc[fieldname] === value) return;
  
  if (isCoreFieldUpdated) {
    const label = getField(fieldname)?.label || fieldname;
    notifyTicketUpdate(label, value as string);
  }
  
  ticket.value.setValue.submit(
    { [fieldname]: value },
    {
      onSuccess: () => {
        if (fieldname === "agent_group") {
          assignees.value.reload();
        }
      },
    }
  );
}
</script>