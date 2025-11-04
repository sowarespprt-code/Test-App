<template>
  <div class="flex flex-col overflow-y-auto">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs" />
      </template>
      <template #right-header>
        <!-- ✅ REMOVED Custom Action Button -->
        <CustomActions
          v-if="template.data?._customActions"
          :actions="template.data?._customActions"
        />
      </template>
    </LayoutHeader>

    <!-- Custom License Details Popup -->
    <div
      v-if="showLicensePopup"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden">
        <!-- Popup Header -->
        <div class="flex items-center justify-between px-5 py-3 border-b bg-gray-50">
          <h2 class="text-lg font-semibold text-gray-800">Customer License Details</h2>
          <button
            @click="showLicensePopup = false"
            class="text-gray-500 hover:text-gray-700 transition"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <!-- Popup Body -->
        <div class="px-5 py-3 overflow-y-auto max-h-[calc(90vh-120px)]">
          <!-- Loading State -->
          <div v-if="licenseLoading" class="flex items-center justify-center py-8">
            <div class="flex flex-col items-center gap-2">
              <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
              <p class="text-sm text-gray-600">Fetching license details...</p>
            </div>
          </div>

          <!-- Error State -->
          <div v-else-if="licenseError" class="p-3 bg-red-50 border border-red-200 rounded-lg">
            <h3 class="text-base font-medium text-red-800 mb-1">Error Loading License Details</h3>
            <p class="text-sm text-red-700">{{ licenseError }}</p>
            <button
              @click="fetchLicenseDetails"
              class="mt-2 px-3 py-1.5 text-sm bg-red-600 hover:bg-red-700 text-white rounded transition"
            >
              Retry
            </button>
          </div>

          <!-- Success State -->
          <div v-else-if="licenseData" class="space-y-3">
            <!-- Customer Code and Name (Same Line) -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <span class="text-xs font-semibold text-gray-600 uppercase tracking-wide">Customer Code</span>
                <p class="mt-0.5 text-sm text-gray-900 font-medium">{{ licenseData.CustomerCode || 'Not available' }}</p>
              </div>
              <div>
                <span class="text-xs font-semibold text-gray-600 uppercase tracking-wide">Customer Name</span>
                <p class="mt-0.5 text-sm text-gray-900 font-medium">{{ licenseData.CustomerName || 'Not available' }}</p>
              </div>
            </div>

            <div class="border-t border-gray-200 my-2"></div>

            <!-- AMC End Date -->
            <div>
              <span class="text-xs font-semibold text-gray-600 uppercase tracking-wide">AMC End Date</span>
              <p
                class="mt-0.5 text-sm font-semibold inline-block px-2 py-1 rounded"
                :class="{
                  'bg-red-100 text-red-800': isExpired(licenseData.AMCEndDate),
                  'bg-yellow-100 text-yellow-800': isExpiringSoon(licenseData.AMCEndDate),
                  'bg-green-100 text-green-800': !isExpired(licenseData.AMCEndDate) && !isExpiringSoon(licenseData.AMCEndDate)
                }"
              >
                {{ formatDate(licenseData.AMCEndDate) }}
              </p>
            </div>

            <!-- License Type and Subscription End Date -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <span class="text-xs font-semibold text-gray-600 uppercase tracking-wide">License Type</span>
                <p class="mt-0.5 text-sm text-gray-900">{{ licenseData.LicenseType || 'Not available' }}</p>
              </div>
              <div>
                <span class="text-xs font-semibold text-gray-600 uppercase tracking-wide">Subscription End Date</span>
                <p
                  class="mt-0.5 text-sm font-semibold inline-block px-2 py-1 rounded"
                  :class="{
                    'bg-red-100 text-red-800': isExpired(licenseData.SubscriptionExpDate),
                    'bg-yellow-100 text-yellow-800': isExpiringSoon(licenseData.SubscriptionExpDate),
                    'bg-green-100 text-green-800': !isExpired(licenseData.SubscriptionExpDate) && !isExpiringSoon(licenseData.SubscriptionExpDate)
                  }"
                >
                  {{ formatDate(licenseData.SubscriptionExpDate) }}
                </p>
              </div>
            </div>

            <div class="border-t border-gray-200 my-2"></div>

            <!-- Address -->
            <div>
              <span class="text-xs font-semibold text-gray-600 uppercase tracking-wide">Address</span>
              <p class="mt-0.5 text-sm text-gray-900">
                {{ [licenseData.Address1, licenseData.Address2].filter(Boolean).join(', ') || 'Not available' }}
              </p>
            </div>

            <!-- Phone and Email -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <span class="text-xs font-semibold text-gray-600 uppercase tracking-wide">Phone</span>
                <p class="mt-0.5 text-sm text-gray-900">
                  {{ [licenseData.Phone1, licenseData.Phone2].filter(Boolean).join(', ') || 'Not available' }}
                </p>
              </div>
              <div>
                <span class="text-xs font-semibold text-gray-600 uppercase tracking-wide">Email</span>
                <p class="mt-0.5 text-sm text-gray-900 break-all">{{ licenseData.EmailID || 'Not available' }}</p>
              </div>
            </div>

            <div class="border-t border-gray-200 my-2"></div>

            <!-- Owner Name and Contact Person -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <span class="text-xs font-semibold text-gray-600 uppercase tracking-wide">Owner Name</span>
                <p class="mt-0.5 text-sm text-gray-900">{{ licenseData.OwnerName || 'Not available' }}</p>
              </div>
              <div>
                <span class="text-xs font-semibold text-gray-600 uppercase tracking-wide">Contact Person</span>
                <p class="mt-0.5 text-sm text-gray-900">{{ licenseData.ContactPerson || 'Not available' }}</p>
              </div>
            </div>

            <div class="border-t border-gray-200 my-2"></div>

            <!-- Nature of Business -->
            <div>
              <span class="text-xs font-semibold text-gray-600 uppercase tracking-wide">Nature of Business (GST)</span>
              <p class="mt-0.5 text-sm text-gray-900">{{ licenseData.NatureOfBusiness || 'Not available' }}</p>
            </div>

            <div class="border-t border-gray-200 my-2"></div>

            <!-- Status Summary -->
            <div class="p-3 rounded-lg" :class="getLicenseStatusClass()">
              <div class="flex items-start gap-2">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="flex-shrink-0 mt-0.5"
                >
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="16" x2="12" y2="12"></line>
                  <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
                <div>
                  <h3 class="text-sm font-semibold mb-0.5">License Status</h3>
                  <p class="text-xs leading-relaxed">{{ getLicenseStatusMessage() }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- No Data State -->
          <div v-else class="p-3 bg-gray-50 border border-gray-200 rounded-lg">
            <p class="text-sm text-gray-600">No license details available. Please select a customer first.</p>
          </div>
        </div>

        <!-- Popup Footer -->
        <div class="flex items-center justify-end gap-2 px-5 py-3 border-t bg-gray-50">
          <Button
            label="Close"
            theme="gray"
            variant="subtle"
            @click="showLicensePopup = false"
          />
          <Button
            v-if="licenseData"
            label="Refresh"
            theme="gray"
            variant="solid"
            :loading="licenseLoading"
            @click="fetchLicenseDetails"
          />
        </div>
      </div>
    </div>

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
          <UniInput
            v-for="field in visibleFields"
            :key="`${field.fieldname}-${templateFields[field.fieldname]}`"
            :field="field"
            :value="templateFields[field.fieldname]"
            @change="
              (e) => handleOnFieldChange(e, field.fieldname, field.fieldtype)
            "
          />
        </div>
       
        <!-- Button Near Customer Fields -->
        <div class="mt-3 flex justify-end">
          <button
            class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm bg-blue-400 hover:bg-blue-500 text-white font-medium rounded transition-colors duration-200 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
            @click="openLicensePopup"
            :disabled="!templateFields.custom_customercode"
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
const hasShownAutoPopup = ref(false);

// License API state
const licenseLoading = ref(false);
const licenseError = ref("");
const licenseData = ref(null);

// ============================================
// LICENSE API FUNCTIONS
// ============================================
async function fetchLicenseDetails() {
  const customerCode = templateFields.custom_customercode;
 
  console.log('fetchLicenseDetails called with customerCode:', customerCode);
 
  if (!customerCode) {
    licenseError.value = "Customer code is required";
    return;
  }

  licenseLoading.value = true;
  licenseError.value = "";
  licenseData.value = null;

  try {
    console.log('Calling API with customer_code:', customerCode);
   
    const data = await call('helpdesk.api.license.get_customer_license_details', {
      customer_code: customerCode
    });

    console.log('API Response:', data);

    if (!data) {
      throw new Error('No license details found for this customer');
    }

    licenseData.value = data;
    console.log('License data stored:', licenseData.value);
   
  } catch (error) {
    console.error('Error fetching license details:', error);
    licenseError.value = error.message || 'Failed to fetch license details. Please try again.';
    licenseData.value = null;
  } finally {
    licenseLoading.value = false;
  }
}

function openLicensePopup() {
  showLicensePopup.value = true;
  fetchLicenseDetails();
}

function getLicenseStatusClass() {
  if (!licenseData.value) return 'bg-gray-50 border border-gray-200';
 
  const amcExpired = isExpired(licenseData.value.AMCEndDate);
  const subExpired = isExpired(licenseData.value.SubscriptionExpDate);
 
  if (amcExpired || subExpired) {
    return 'bg-red-50 border border-red-200 text-red-800';
  } else if (isExpiringSoon(licenseData.value.AMCEndDate)) {
    return 'bg-yellow-50 border border-yellow-200 text-yellow-800';
  }
 
  return 'bg-green-50 border border-green-200 text-green-800';
}

function getLicenseStatusMessage() {
  if (!licenseData.value) return 'No license information available';
 
  const amcExpired = isExpired(licenseData.value.AMCEndDate);
  const subExpired = isExpired(licenseData.value.SubscriptionExpDate);
  const amcExpiringSoon = isExpiringSoon(licenseData.value.AMCEndDate);
 
  if (amcExpired && subExpired) {
    return 'Both AMC and Subscription have expired. Please contact support for renewal.';
  } else if (amcExpired) {
    return `AMC expired on ${formatDate(licenseData.value.AMCEndDate)}. Please renew to continue receiving support.`;
  } else if (subExpired) {
    return `Subscription expired on ${formatDate(licenseData.value.SubscriptionExpDate)}.`;
  } else if (amcExpiringSoon) {
    return `AMC is expiring soon on ${formatDate(licenseData.value.AMCEndDate)}. Consider renewing.`;
  }
 
  return `AMC is active until ${formatDate(licenseData.value.AMCEndDate)}`;
}

function formatDate(dateString) {
  if (!dateString) return 'Not available';
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  } catch {
    return dateString;
  }
}

function isExpired(dateString) {
  if (!dateString) return false;
  try {
    const date = new Date(dateString);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return date < today;
  } catch {
    return false;
  }
}

function isExpiringSoon(dateString) {
  if (!dateString) return false;
  try {
    const date = new Date(dateString);
    const today = new Date();
    const daysUntilExpiry = Math.floor((date - today) / (1000 * 60 * 60 * 24));
    return daysUntilExpiry > 0 && daysUntilExpiry <= 30;
  } catch {
    return false;
  }
}

// ============================================
// WATCHERS FOR AUTO-POPUP
// ============================================
watch(
  () => [
    templateFields.custom_customer_name,
    templateFields.custom_customercode
  ],
  ([name, code], [oldName, oldCode]) => {
    if (name && code && (name !== oldName || code !== oldCode)) {
      openLicensePopup();
    }
  }
);

// ============================================
// TEMPLATE RESOURCE
// ============================================
const template = createResource({
  url: "helpdesk.helpdesk.doctype.hd_ticket_template.api.get_one",
  makeParams: () => ({
    name: props.templateId || "Default",
  }),
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
  if (f.fieldtype === "Select") {
    handleSelectFieldUpdate(f, fieldname, filters, templateFields, oldFields);
  } else if (f.fieldtype === "Link") {
    handleLinkFieldUpdate(f, fieldname, filters, templateFields, oldFields);
  }
}

const customOnChange = computed(() => template.data?._customOnChange);

const visibleFields = computed(() => {
  let _fields = template.data?.fields?.filter(
    (f) => !isCustomerPortal.value || !f.hide_from_customer
  );
  if (!_fields) return [];
  return _fields.map((field) => parseField(field, templateFields));
});

// ============================================
// AUTO-FETCH FUNCTIONS
// ============================================
async function fetchCustomerName(customerCode) {
  if (!customerCode || isFetchingCustomerName.value) return;
  isFetchingCustomerName.value = true;

  try {
    console.log('Fetching customer for code:', customerCode);
   
    const result = await call('frappe.client.get_list', {
      doctype: 'HD Customer',
      filters: { custom_customercode: customerCode },
      fields: ['name', 'customer_name'],
      limit: 1
    });

    console.log('Fetch result:', result);

    if (result && result.length > 0) {
      const customer = result[0];
      await nextTick();
      templateFields.custom_customer_name = customer.name;
      console.log('Customer name field set to:', customer.name);
      await nextTick();
      fetchProductName(customer.name);
    } else {
      templateFields.custom_customer_name = '';
      templateFields.custom_product = '';
      console.warn('No customer found for code:', customerCode);
    }
  } catch (error) {
    console.error('Error fetching customer name:', error);
    templateFields.custom_customer_name = '';
    templateFields.custom_product = '';
  } finally {
    isFetchingCustomerName.value = false;
  }
}

async function fetchCustomerCode(customerName) {
  if (!customerName || isFetchingCustomerCode.value) return;
  isFetchingCustomerCode.value = true;

  try {
    console.log('Fetching customer code for:', customerName);
   
    const result = await call('frappe.client.get_value', {
      doctype: 'HD Customer',
      filters: { name: customerName },
      fieldname: ['custom_customercode']
    });

    console.log('Fetch customer code result:', result);
   
    let customerCode = null;
    if (result?.message?.custom_customercode) {
      customerCode = result.message.custom_customercode;
    } else if (result?.custom_customercode) {
      customerCode = result.custom_customercode;
    }

    console.log('Extracted customer code:', customerCode);

    if (customerCode) {
      await nextTick();
      templateFields.custom_customercode = customerCode;
      console.log('✅ Customer code field set to:', customerCode);
      await nextTick();
    } else {
      templateFields.custom_customercode = '';
      console.warn('❌ No customer code found for:', customerName);
    }
  } catch (error) {
    console.error('Error fetching customer code:', error);
    templateFields.custom_customercode = '';
  } finally {
    isFetchingCustomerCode.value = false;
  }
}

async function fetchProductName(customerName) {
  if (!customerName || isFetchingProductName.value) return;
  isFetchingProductName.value = true;

  try {
    console.log('Fetching product name for customer:', customerName);
   
    const result = await call('frappe.client.get_value', {
      doctype: 'HD Customer',
      filters: { name: customerName },
      fieldname: ['custom_productname']
    });

    console.log('Fetch product name result:', result);
   
    let productName = null;
    if (result?.message?.custom_productname) {
      productName = result.message.custom_productname;
    } else if (result?.custom_productname) {
      productName = result.custom_productname;
    }

    console.log('Extracted product name:', productName);

    if (productName) {
      await nextTick();
      templateFields.custom_product = productName;
      console.log('✅ custom_product field set to:', productName);
      await nextTick();
    } else {
      templateFields.custom_product = '';
      console.warn('❌ No product name found for customer:', customerName);
    }
  } catch (error) {
    console.error('Error fetching product name:', error);
    templateFields.custom_product = '';
  } finally {
    isFetchingProductName.value = false;
  }
}

// ============================================
// FIELD CHANGE HANDLER
// ============================================
function handleOnFieldChange(e: any, fieldname: string, fieldtype: string) {
  const newValue = e.value;
  templateFields[fieldname] = newValue;

  if (fieldname === 'custom_customercode' && newValue) {
    console.log('Customer code changed to:', newValue);
    fetchCustomerName(newValue);
  }
 
  if (fieldname === 'custom_customer_name' && newValue) {
    console.log('Customer name changed to:', newValue);
    fetchCustomerCode(newValue);
    fetchProductName(newValue);
  }
 
  const fieldDependentFns = customOnChange.value?.[fieldname];
  if (fieldDependentFns) {
    fieldDependentFns.forEach((fn: Function) => {
      fn(newValue, fieldtype);
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
    const toVerify = [...fields, "subject", "description"];
    for (const field of toVerify) {
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
    if (isManager) {
      updateOnboardingStep("create_first_ticket", true, false, () =>
        localStorage.setItem("firstTicket", data.name)
      );
    }
    if (isCustomerPortal.value) {
      capture("new_ticket_submitted", {
        data: {
          user: userID,
          ticketID: data.name,
          subject: subject.value,
          description: description.value,
          customFields: templateFields,
        },
      });
    }
  },
});

// ============================================
// UTILITIES
// ============================================
function sanitize(html: string) {
  return sanitizeHtml(html, {
    allowedTags: sanitizeHtml.defaults.allowedTags.concat(["img"]),
  });
}

const breadcrumbs = computed(() => [
  {
    label: "Tickets",
    route: {
      name: isCustomerPortal.value ? "TicketsCustomer" : "TicketsAgent",
    },
  },
  {
    label: "New Ticket",
    route: { name: "TicketNew" },
  },
]);

usePageMeta(() => ({ title: "New Ticket" }));

onMounted(() => {
  capture("new_ticket_page", { data: { user: userID } });
});
</script>