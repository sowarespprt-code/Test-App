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

    <!-- Custom License Details Popup -->
    <div
      v-if="showLicensePopup"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-hidden">
        <!-- Popup Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b bg-gray-50">
          <h2 class="text-xl font-semibold text-gray-800">Customer License Details</h2>
          <button
            @click="showLicensePopup = false"
            class="text-gray-500 hover:text-gray-700 transition"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
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
        <div class="px-6 py-4 overflow-y-auto max-h-[calc(90vh-140px)]">
          <!-- Loading State -->
          <div v-if="licenseLoading" class="flex items-center justify-center py-12">
            <div class="flex flex-col items-center gap-3">
              <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
              <p class="text-gray-600">Fetching license details...</p>
            </div>
          </div>

          <!-- Error State -->
          <div v-else-if="licenseError" class="p-4 bg-red-50 border border-red-200 rounded-lg">
            <h3 class="text-lg font-medium text-red-800 mb-2">Error Loading License Details</h3>
            <p class="text-sm text-red-700">{{ licenseError }}</p>
            <button
              @click="fetchLicenseDetails"
              class="mt-3 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded transition"
            >
              Retry
            </button>
          </div>

          <!-- Success State -->
          <div v-else-if="licenseData">
            <!-- Customer Information -->
            <div class="mb-6">
              <h3 class="text-lg font-medium text-gray-700 mb-3 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
                Customer Information
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">Customer Code</label>
                  <input
                    type="text"
                    :value="licenseData.CustomerCode || 'Not available'"
                    readonly
                    class="w-full text-gray-900 bg-gray-50 px-3 py-2 rounded border border-gray-300 focus:outline-none"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">Customer Name</label>
                  <input
                    type="text"
                    :value="licenseData.CustomerName || 'Not available'"
                    readonly
                    class="w-full text-gray-900 bg-gray-50 px-3 py-2 rounded border border-gray-300 focus:outline-none"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">Owner Name</label>
                  <input
                    type="text"
                    :value="licenseData.OwnerName || 'Not available'"
                    readonly
                    class="w-full text-gray-900 bg-gray-50 px-3 py-2 rounded border border-gray-300 focus:outline-none"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">Contact Person</label>
                  <input
                    type="text"
                    :value="licenseData.ContactPerson || 'Not available'"
                    readonly
                    class="w-full text-gray-900 bg-gray-50 px-3 py-2 rounded border border-gray-300 focus:outline-none"
                  />
                </div>
              </div>
            </div>

            <!-- Contact Information -->
            <div class="mb-6">
              <h3 class="text-lg font-medium text-gray-700 mb-3 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                </svg>
                Contact Information
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">Phone 1</label>
                  <input
                    type="text"
                    :value="licenseData.Phone1 || 'Not available'"
                    readonly
                    class="w-full text-gray-900 bg-gray-50 px-3 py-2 rounded border border-gray-300 focus:outline-none"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">Phone 2</label>
                  <input
                    type="text"
                    :value="licenseData.Phone2 || 'Not available'"
                    readonly
                    class="w-full text-gray-900 bg-gray-50 px-3 py-2 rounded border border-gray-300 focus:outline-none"
                  />
                </div>
                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-600 mb-1">Email</label>
                  <input
                    type="text"
                    :value="licenseData.EmailID || 'Not available'"
                    readonly
                    class="w-full text-gray-900 bg-gray-50 px-3 py-2 rounded border border-gray-300 focus:outline-none"
                  />
                </div>
              </div>
            </div>

            <!-- Address Information -->
            <div class="mb-6">
              <h3 class="text-lg font-medium text-gray-700 mb-3 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                  <circle cx="12" cy="10" r="3"></circle>
                </svg>
                Address Information
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">Address Line 1</label>
                  <input
                    type="text"
                    :value="licenseData.Address1 || 'Not available'"
                    readonly
                    class="w-full text-gray-900 bg-gray-50 px-3 py-2 rounded border border-gray-300 focus:outline-none"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">Address Line 2</label>
                  <input
                    type="text"
                    :value="licenseData.Address2 || 'Not available'"
                    readonly
                    class="w-full text-gray-900 bg-gray-50 px-3 py-2 rounded border border-gray-300 focus:outline-none"
                  />
                </div>
                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-600 mb-1">Nature of Business (GST)</label>
                  <input
                    type="text"
                    :value="licenseData.NatureOfBusiness || 'Not available'"
                    readonly
                    class="w-full text-gray-900 bg-gray-50 px-3 py-2 rounded border border-gray-300 focus:outline-none"
                  />
                </div>
              </div>
            </div>

            <!-- License Details -->
            <div class="mb-6">
              <h3 class="text-lg font-medium text-gray-700 mb-3 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                </svg>
                License & Subscription Information
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">License Type</label>
                  <input
                    type="text"
                    :value="licenseData.LicenseType || 'Not available'"
                    readonly
                    class="w-full text-gray-900 bg-gray-50 px-3 py-2 rounded border border-gray-300 focus:outline-none"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">Subscription Expiry Date</label>
                  <input
                    type="text"
                    :value="formatDate(licenseData.SubscriptionExpDate)"
                    readonly
                    class="w-full text-gray-900 bg-gray-50 px-3 py-2 rounded border border-gray-300 focus:outline-none"
                    :class="{
                      'bg-red-50 border-red-300 text-red-800': isExpired(licenseData.SubscriptionExpDate),
                      'bg-green-50 border-green-300 text-green-800': !isExpired(licenseData.SubscriptionExpDate)
                    }"
                  />
                </div>
                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-600 mb-1">Subscription Remarks</label>
                  <input
                    type="text"
                    :value="licenseData.SubscriptionRemarks || 'Not available'"
                    readonly
                    class="w-full text-gray-900 bg-gray-50 px-3 py-2 rounded border border-gray-300 focus:outline-none"
                  />
                </div>
              </div>
            </div>

            <!-- AMC Information -->
            <div class="mb-6">
              <h3 class="text-lg font-medium text-gray-700 mb-3 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="16" y1="2" x2="16" y2="6"></line>
                  <line x1="8" y1="2" x2="8" y2="6"></line>
                  <line x1="3" y1="10" x2="21" y2="10"></line>
                </svg>
                AMC (Annual Maintenance Contract) Information
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">AMC Start Date</label>
                  <input
                    type="text"
                    :value="formatDate(licenseData.AMCStartDate)"
                    readonly
                    class="w-full text-gray-900 bg-gray-50 px-3 py-2 rounded border border-gray-300 focus:outline-none"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">AMC End Date</label>
                  <input
                    type="text"
                    :value="formatDate(licenseData.AMCEndDate)"
                    readonly
                    class="w-full text-gray-900 bg-gray-50 px-3 py-2 rounded border border-gray-300 focus:outline-none"
                    :class="{
                      'bg-red-50 border-red-300 text-red-800': isExpired(licenseData.AMCEndDate),
                      'bg-yellow-50 border-yellow-300 text-yellow-800': isExpiringSoon(licenseData.AMCEndDate),
                      'bg-green-50 border-green-300 text-green-800': !isExpired(licenseData.AMCEndDate) && !isExpiringSoon(licenseData.AMCEndDate)
                    }"
                  />
                </div>
              </div>
            </div>

            <!-- Status Summary -->
            <div class="p-4 rounded-lg" :class="getLicenseStatusClass()">
              <div class="flex items-start gap-3">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
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
                  <h3 class="text-lg font-medium mb-1">License Status</h3>
                  <p class="text-sm">{{ getLicenseStatusMessage() }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- No Data State -->
          <div v-else class="p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <p class="text-gray-600">No license details available. Please select a customer first.</p>
          </div>
        </div>

        <!-- Popup Footer -->
        <div class="flex items-center justify-end gap-3 px-6 py-4 border-t bg-gray-50">
          <Button
            label="Close"
            theme="gray"
            variant="subtle"
            @click="showLicensePopup = false"
          />
          <Button
            v-if="licenseData"
            label="Refresh License"
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
// STATE
// ============================================
const subject = ref("");
const description = ref("");
const attachments = ref([]);
const templateFields = reactive({});
const isFetchingCustomerName = ref(false);
const isFetchingCustomerCode = ref(false);
const showLicensePopup = ref(false);
const hasShownAutoPopup = ref(false);

// License API state
const licenseLoading = ref(false);
const licenseError = ref("");
const licenseData = ref(null);

// ============================================
// LICENSE API INTEGRATION
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
    console.error('Error stack:', error.stack);
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
// WATCH FOR CUSTOMER SELECTION - AUTO POPUP
// ============================================
watch(
  () => templateFields.custom_customer_name,
  async (newValue, oldValue) => {
    // When customer is selected, wait for customer code to be fetched, then show popup
    if (newValue && newValue !== oldValue) {
      // Wait a bit for customer code to be fetched
      setTimeout(() => {
        if (templateFields.custom_customercode) {
          openLicensePopup();
        }
      }, 500);
    }
  }
);

watch(
  () => templateFields.custom_customercode,
  async (newValue, oldValue) => {
    // When customer code is selected directly, show popup
    if (newValue && newValue !== oldValue) {
      // Wait a bit for customer name to be fetched
      setTimeout(() => {
        if (templateFields.custom_customer_name) {
          openLicensePopup();
        }
      }, 500);
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
// AUTO-FETCH CUSTOMER NAME / CODE LOGIC
// ============================================
async function fetchCustomerName(customerCode) {
  if (!customerCode || isFetchingCustomerName.value) return;
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
      await nextTick();
      templateFields.custom_customer_name = customer.name;
      await nextTick();
    } else {
      templateFields.custom_customer_name = "";
    }
  } catch (error) {
    console.error("Error fetching customer name:", error);
    templateFields.custom_customer_name = "";
  } finally {
    isFetchingCustomerName.value = false;
  }
}

async function fetchCustomerCode(customerName) {
  if (!customerName || isFetchingCustomerCode.value) return;
  isFetchingCustomerCode.value = true;

  try {
    const result = await call("frappe.client.get_value", {
      doctype: "HD Customer",
      filters: { name: customerName },
      fieldname: ["custom_customercode"],
    });

    let customerCode = null;
    if (result?.message?.custom_customercode) {
      customerCode = result.message.custom_customercode;
    } else if (result?.custom_customercode) {
      customerCode = result.custom_customercode;
    }

    if (customerCode) {
      await nextTick();
      templateFields.custom_customercode = customerCode;
      await nextTick();
    } else {
      templateFields.custom_customercode = "";
    }
  } catch (error) {
    console.error("Error fetching customer code:", error);
    templateFields.custom_customercode = "";
  } finally {
    isFetchingCustomerCode.value = false;
  }
}

function handleOnFieldChange(e: any, fieldname: string, fieldtype: string) {
  const newValue = e.value;
  templateFields[fieldname] = newValue;

  if (fieldname === "custom_customercode" && newValue) {
    fetchCustomerName(newValue);
  }

  if (fieldname === "custom_customer_name" && newValue) {
    fetchCustomerCode(newValue);
  }

  const fieldDependentFns = customOnChange.value?.[fieldname];
  if (fieldDependentFns) {
    fieldDependentFns.forEach((fn: Function) => {
      fn(newValue, fieldtype);
    });
  }
}

// ============================================
// TICKET CREATION LOGIC
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
// MISC
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