<template>
  <div class="flex flex-col overflow-y-auto">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs" />
      </template>
      <template #right-header>
        <CustomActions
          v-if="template.data?._customActions"
          :actions="template.data?._customActions"
        />
      </template>
    </LayoutHeader>

    <!-- Reusable License Details Popup -->
    <LicenseDetailsPopup
      v-model="showLicensePopup"
      :customer-code="templateFields.custom_customercode || ''"
      @licenseLoaded="handleLicenseLoaded"
    />

    <!-- Main Container -->
    <div
      class="flex flex-col gap-5 py-6 h-full flex-1 self-center overflow-auto mx-auto w-full max-w-4xl px-5"
    >
      <!-- custom fields descriptions -->
      <div v-if="Boolean(template.data?.about)" class="">
        <div class="prose-f" v-html="sanitize(template.data.about)" />
      </div>

      <!-- custom fields -->
      <div v-if="Boolean(visibleFields)">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <template v-for="field in visibleFields" :key="field.fieldname">
            <!-- CUSTOMER CODE FIELD -->
            <UniInput
              v-if="field.fieldname === 'custom_customercode'"
              :field="field"
              :value="templateFields[field.fieldname]"
          
              @input="handleCustomerCodeInput"
              @keydown.enter.prevent="event => handleCustomerCodeEnter(event)"
              @blur="handleCustomerCodeBlur"
            />
           
            <!-- CUSTOMER NAME FIELD -->
            <UniInput
              v-else-if="field.fieldname === 'custom_customer_name'"
              :field="field"
              :value="templateFields[field.fieldname]"
              @change="(value) => handleOnFieldChange(value, field.fieldname, field.fieldtype)"
              @input="(e) => safeSetField(field.fieldname, e)"   
            />

            <!-- ALL OTHER FIELDS -->
            <UniInput
              v-else
              :field="field"
              :value="templateFields[field.fieldname]"
              @input="(e) => safeSetField(field.fieldname, e)" 
            />
          </template>
        </div>

        <!-- Button Near Customer Fields -->
        <div class="mt-3 flex justify-end">
          <button
            class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm bg-blue-400 hover:bg-blue-500 text-white font-medium rounded transition-colors duration-200 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
            @click="openLicensePopup"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            View License Details
          </button>
        </div>
      </div>

      <!-- existing fields -->
      <div
        class="flex flex-col"
        :class="(subject.length >= 2 || description.length) && 'gap-5'"
      >
        <div class="flex flex-col gap-2">
          <span class="block text-sm text-gray-700">
            Subject
            <span class="place-self-center text-red-500"> * </span>
          </span>
          <FormControl
            v-model="subject"
            type="text"
            placeholder="A short description"
          />
        </div>
        <SearchArticles
          v-if="isCustomerPortal"
          :query="subject"
          class="shadow"
        />
        <div v-if="isCustomerPortal">
          <h4
            v-show="subject.length <= 2 && description.length === 0"
            class="text-p-sm text-gray-500 ml-1"
          >
            Please enter a subject to continue
          </h4>
          <TicketTextEditor
            v-show="subject.length > 2 || description.length > 0"
            ref="editor"
            v-model:attachments="attachments"
            v-model:content="description"
            placeholder="Detailed explanation"
            expand
            :uploadFunction="(file:any)=>uploadFunction(file)"
          >
            <template #bottom-right>
              <Button
                label="Submit"
                theme="gray"
                variant="solid"
                :disabled="
                  $refs.editor.editor.isEmpty || ticket.loading || !subject
                "
                @click="() => ticket.submit()"
              />
            </template>
          </TicketTextEditor>
        </div>
      </div>

      <!-- for agent portal -->
      <div v-if="!isCustomerPortal">
        <TicketTextEditor
          ref="editor"
          v-model:attachments="attachments"
          v-model:content="description"
          placeholder="Detailed explanation"
          expand
        >
          <template #bottom-right>
            <Button
              label="Submit"
              theme="gray"
              variant="solid"
              :disabled="
                $refs.editor.editor.isEmpty || ticket.loading || !subject
              "
              @click="() => ticket.submit()"
            />
          </template>
        </TicketTextEditor>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { LayoutHeader, UniInput } from "@/components";
import LicenseDetailsPopup from "@/components/LicenseDetailsPopup.vue"; // Import the new component
import {
  handleLinkFieldUpdate,
  handleSelectFieldUpdate,
  parseField,
  setupCustomizations,
} from "@/composables/formCustomisation";
import { useAuthStore } from "@/stores/auth";
import { globalStore } from "@/stores/globalStore";
import { capture } from "@/telemetry";
import { Field } from "@/types";
import { isCustomerPortal, uploadFunction } from "@/utils";
import {
  Breadcrumbs,
  Button,
  call,
  createResource,
  FormControl,
  usePageMeta,
} from "frappe-ui";
import { useOnboarding } from "frappe-ui/frappe";
import { isEmpty } from "lodash";
import sanitizeHtml from "sanitize-html";
import { computed, onMounted, reactive, ref, nextTick, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import SearchArticles from "../../components/SearchArticles.vue";
import TicketTextEditor from "./TicketTextEditor.vue";

interface P {
  templateId?: string;
}

const props = withDefaults(defineProps<P>(), {
  templateId: "",
});

const route = useRoute();
const router = useRouter();
const { $dialog } = globalStore();
const { updateOnboardingStep } = useOnboarding("helpdesk");
const { isManager, userId: userID } = useAuthStore();

// ============================================
// STATE DECLARATIONS
// ============================================
const subject = ref("");
const description = ref("");
const attachments = ref([]);
const templateFields = reactive({});
const isFetchingCustomerName = ref(false);
const isFetchingCustomerCode = ref(false);
const isFetchingProductName = ref(false);
const showLicensePopup = ref(false);
const licenseLoading = ref(false);
const licenseError = ref("");
const licenseData = ref(null);
const lastValidatedCustomerCode = ref("");
const MIN_CODE_LENGTH = 3;
const invalidCodeError = ref("");
const customerCode = ref("");

// Flags to prevent circular event triggering
const isUpdatingInternally = ref(false);
const isManuallySelectingCustomer = ref(false);

// ============================================
// UTILITY FUNCTIONS
// ============================================
function extractValue(payload: any): string {
  if (payload == null || payload === undefined) return "";
  if (typeof payload === "string" || typeof payload === "number") {
    return String(payload).trim();
  }
  if (typeof payload === "object" && "value" in payload) {
    return String(payload.value || "").trim();
  }
  if (typeof payload === "object" && payload.target && "value" in payload.target) {
    return String(payload.target.value || "").trim();
  }
  return "";
}

function safeSetField(fieldname: string, payload: any) {
  const value = extractValue(payload);
  if (templateFields[fieldname] !== value) {
    templateFields[fieldname] = value;
  }
}

// ============================================
// LICENSE POPUP HANDLERS
// ============================================
async function openLicensePopup() {
  // 🟢 FIX 1: Wait for Vue to flush reactivity before reading the field
  await nextTick();

  const customerCode = extractValue(templateFields.custom_customercode)?.trim() || 
                       document.querySelector('[name="custom_customercode"]')?.value?.trim() || "";
  console.log("🟢 Fetched customer code before popup:", customerCode);

  // 🟢 FIX 2: Ensure valid value is actually present
  if (!customerCode || customerCode === "") {
    $dialog({
      title: "Customer Code Required",
      message: "Please enter a valid Customer Code first.",
    });
    return;
  }

  if (customerCode.length < MIN_CODE_LENGTH) {
    $dialog({
      title: "Invalid Customer Code",
      message: `Customer Code must be at least ${MIN_CODE_LENGTH} characters.`,
    });
    return;
  }

  // 🟢 FIX 3: Validate customer existence before showing popup
  const found = await fetchCustomerName(customerCode);
  if (found) {
    lastValidatedCustomerCode.value = customerCode;
    showLicensePopup.value = true; // ✅ Correct popup for valid code
  } else {
    $dialog({
      title: "Invalid Customer Code",
      message: "No customer found for this code. Please check and try again.",
    });

    isUpdatingInternally.value = true;
    safeSetField("custom_customer_name", "");
    safeSetField("custom_product", "");
    isUpdatingInternally.value = false;
    showLicensePopup.value = false;
  }
}


// ============================================
// WATCHERS - FIXED TO PREVENT CIRCULAR TRIGGERS
// ============================================
watch(
  () => templateFields.custom_customer_name,
  (newName, oldName) => {
    // Skip if we're updating internally to prevent circular triggers
    if (isUpdatingInternally.value || isManuallySelectingCustomer.value) return;
    
    const cleanName = extractValue(newName);
    
    // If customer name is cleared, clear all related fields
    if (!cleanName) {
      isUpdatingInternally.value = true;
      safeSetField("custom_customercode", "");
      safeSetField("custom_product", "");
      lastValidatedCustomerCode.value = "";
      licenseData.value = null;
      licenseError.value = "";
      showLicensePopup.value = false;
      isUpdatingInternally.value = false;
    }
  }
);

// ============================================
// TEMPLATE RESOURCE
// ============================================
const template = createResource({
  url: "helpdesk.helpdesk.doctype.hd_ticket_template.api.get_one",
  makeParams: () => ({ name: props.templateId || "Default" }),
  auto: true,
  onSuccess: (data) => {
    description.value = data.description_template || "";
    oldFields = window.structuredClone(data.fields || []);
    setupCustomizations(template, {
      doc: templateFields,
      call,
      router,
      $dialog,
      applyFilters,
    });
    setupTemplateFields(data.fields);
  },
});

function setupTemplateFields(fields) {
  fields.forEach((field: Field) => {
    templateFields[field.fieldname] = "";
  });
}

let oldFields = [];

function applyFilters(fieldname: string, filters: any = null) {
  const f: Field = template.data.fields.find((f) => f.fieldname === fieldname);
  if (!f) return;
  if (f.fieldtype === "Select")
    handleSelectFieldUpdate(f, fieldname, filters, templateFields, oldFields);
  else if (f.fieldtype === "Link")
    handleLinkFieldUpdate(f, fieldname, filters, templateFields, oldFields);
}

const customOnChange = computed(() => template.data?._customOnChange);

const visibleFields = computed(() => {
  const _fields = template.data?.fields?.filter(
    (f) => !isCustomerPortal.value || !f.hide_from_customer
  );
  return _fields?.map((f) => parseField(f, templateFields)) || [];
});

// ============================================
// CUSTOMER CODE INPUT HANDLER
// ============================================
function handleCustomerCodeInput(event: any) {
  const value = event.target?.value?.trim() || "";
  safeSetField("custom_customercode", value);
}

// ============================================
// CUSTOMER CODE HANDLERS
// ============================================
async function handleCustomerCodeEnter(event: any) {
  const enteredCode = event.target.value?.trim();
  const previousCode = lastValidatedCustomerCode.value?.trim();
  invalidCodeError.value = "";

  // 1️⃣ If empty
  if (!enteredCode) {
    isUpdatingInternally.value = true;
    safeSetField("custom_customer_name", "");
    safeSetField("custom_product", "");
    licenseData.value = null;
    showLicensePopup.value = false;
    isUpdatingInternally.value = false;
    return;
  }

  if (enteredCode.length < MIN_CODE_LENGTH) {
    $dialog({
      title: 'Invalid Customer Code',
      message: `Customer Code must be at least ${MIN_CODE_LENGTH} characters.`,
    });
    return;
  }

  // 2️⃣ Skip re-fetch if same valid code
  if (enteredCode === previousCode) {
    showLicensePopup.value = true;
    return;
  }

  safeSetField("custom_customercode", enteredCode);

  // 3️⃣ Fetch customer details
  const found = await fetchCustomerName(enteredCode);
  if (found) {
    lastValidatedCustomerCode.value = enteredCode;

    // 🟢 FIX: Directly show license popup for valid customer
    showLicensePopup.value = true;
  } else {
    // 🔴 FIX: Proper invalid popup when pressing Enter with invalid code
    $dialog({
      title: 'Invalid Customer Code',
      message: 'No customer found for this code. Please check and try again.',
    });

    isUpdatingInternally.value = true;
    safeSetField("custom_customer_name", "");
    safeSetField("custom_product", "");
    licenseData.value = null;
    showLicensePopup.value = false;
    isUpdatingInternally.value = false;
  }
}

async function handleLicenseButtonClick() {
  const customerCode = extractValue(templateFields.custom_customercode);
  
  if (!customerCode) {
    licenseError.value = "Please enter a valid Customer Code first.";
    showLicensePopup.value = false;
    return;
  }
  
  if (customerCode.length < MIN_CODE_LENGTH) {
    licenseError.value = `Customer Code must be at least ${MIN_CODE_LENGTH} characters.`;
    showLicensePopup.value = false;
    return;
  }
  
  // Only fetch if code changed or we don't have customer name
  if (customerCode !== lastValidatedCustomerCode.value || !templateFields.custom_customer_name) {
    const found = await fetchCustomerName(customerCode);
    if (found) {
      lastValidatedCustomerCode.value = customerCode;
      await openLicensePopup();
      showLicensePopup.value = true;
    } else {
      licenseError.value = "No customer found for this code.";
      isUpdatingInternally.value = true;
      safeSetField("custom_customer_name", "");
      safeSetField("custom_product", "");
      showLicensePopup.value = false;
      isUpdatingInternally.value = false;
    }
  } else {
    // Already validated, just fetch license and show popup
    await openLicensePopup();
    showLicensePopup.value = true;
  }
}


// ============================================
// AUTO-FETCH FUNCTIONS
// ============================================
async function fetchCustomerName(customerCode: string) {
  if (!customerCode || isFetchingCustomerName.value) return false;
 
  isFetchingCustomerName.value = true;
  try {
    const result = await call("frappe.client.get_list", {
      doctype: "HD Customer",
      filters: { custom_customercode: customerCode },
      fields: ["name", "customer_name"],
      limit: 1,
    });
   
    if (result && result.length > 0) {
      const customer = result[0];
      isUpdatingInternally.value = true;
      await nextTick();
      safeSetField("custom_customer_name", customer.name);
      await nextTick();
      await fetchProductName(customer.name);
      isUpdatingInternally.value = false;
      return true;
    } else {
      return false;
    }
  } catch (error) {
    console.error("Error fetching customer:", error);
    return false;
  } finally {
    isFetchingCustomerName.value = false;
  }
}

async function fetchCustomerCode(customerName: string) {
  if (!customerName || isFetchingCustomerCode.value) return;
 
  isFetchingCustomerCode.value = true;
  try {
    const result = await call("frappe.client.get_value", {
      doctype: "HD Customer",
      filters: { name: customerName },
      fieldname: ["custom_customercode"],
    });
   
    const code = result?.message?.custom_customercode || result?.custom_customercode;
    if (code) {
      isUpdatingInternally.value = true;
      await nextTick();
      safeSetField("custom_customercode", code);
      lastValidatedCustomerCode.value = code;
      await nextTick();
      isUpdatingInternally.value = false;
    }
  } catch (error) {
    console.error("Error fetching customer code:", error);
  } finally {
    isFetchingCustomerCode.value = false;
  }
}

async function fetchProductName(customerName: string) {
  if (!customerName || isFetchingProductName.value) return;
 
  isFetchingProductName.value = true;
  try {
    const result = await call("frappe.client.get_value", {
      doctype: "HD Customer",
      filters: { name: customerName },
      fieldname: ["custom_productname"],
    });
   
    const product = result?.message?.custom_productname || result?.custom_productname;
    safeSetField("custom_product", product || "");
  } catch (error) {
    console.error("Error fetching product name:", error);
  } finally {
    isFetchingProductName.value = false;
  }
}

// ============================================
// FIELD CHANGE HANDLER
// ============================================
async function handleOnFieldChange(payload: any, fieldname: string, fieldtype: string) {
  if (isUpdatingInternally.value) return;
 
  const newValue = extractValue(payload);
  safeSetField(fieldname, newValue);
 
  if (fieldname === "custom_customer_name" && newValue) {
    isManuallySelectingCustomer.value = true;
    await fetchCustomerCode(newValue);
    await fetchProductName(newValue);
    isManuallySelectingCustomer.value = false;
  }
 
  const fieldFns = customOnChange.value?.[fieldname];
  if (fieldFns) {
    fieldFns.forEach((fn: Function) => {
      try {
        fn(newValue, fieldtype);
      } catch (err) {
        console.error("Error in custom onChange:", err);
      }
    });
  }
}

// ============================================
// TICKET CREATION
// ============================================
const ticket = createResource({
  url: "helpdesk.helpdesk.doctype.hd_ticket.api.new",
  debounce: 300,
  makeParams: () => ({
    doc: {
      description: description.value,
      subject: subject.value,
      template: props.templateId,
      ...templateFields,
    },
    attachments: attachments.value,
  }),
  validate: (params) => {
    const fields = visibleFields.value?.filter((f) => f.required) || [];
    for (const field of [...fields, "subject", "description"]) {
      if (isEmpty(params.doc[field.fieldname || field])) {
        return `${field.label || field} is required`;
      }
    }
  },
  onSuccess: (data) => {
    router.push({
      name: isCustomerPortal.value ? "TicketCustomer" : "TicketAgent",
      params: { ticketId: data.name },
    });
    if (isManager)
      updateOnboardingStep("create_first_ticket", true, false, () =>
        localStorage.setItem("firstTicket", data.name)
      );
    if (isCustomerPortal.value)
      capture("new_ticket_submitted", {
        data: { user: userID, ticketID: data.name, subject: subject.value },
      });
  },
});

// ============================================
// UTILITIES & SETUP
// ============================================
function sanitize(html: string) {
  return sanitizeHtml(html, { allowedTags: sanitizeHtml.defaults.allowedTags.concat(["img"]) });
}

const breadcrumbs = computed(() => [
  {
    label: "Tickets",
    route: { name: isCustomerPortal.value ? "TicketsCustomer" : "TicketsAgent" },
  },
  { label: "New Ticket", route: { name: "TicketNew" } },
]);

usePageMeta(() => ({ title: "New Ticket" }));

onMounted(() => {
  capture("new_ticket_page", { data: { user: userID } });
});
</script>