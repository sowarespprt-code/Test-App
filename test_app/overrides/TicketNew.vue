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

    <!-- Customer Search Popup Component -->
    <CustomerSearchPopup
      v-model="showCustomerSearchPopup"
      @customerSelected="handleCustomerSelected"
    />

    <!-- Duplicate Ticket Warning Popup -->
    <div
      v-if="showDuplicateWarning"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      @click.self="closeDuplicateWarning"
    >
      <div class="relative bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] overflow-hidden">
        <!-- Close Button -->
        <button
          @click="closeDuplicateWarning"
          class="absolute top-4 right-4 z-10 p-2 rounded-full hover:bg-gray-100 transition-colors"
          title="Close"
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

        <!-- Header -->
        <div class="bg-yellow-50 border-b border-yellow-200 px-6 py-4">
          <div class="flex items-center gap-3">
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
              class="text-yellow-600"
            >
              <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path>
              <line x1="12" y1="9" x2="12" y2="13"></line>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
            <div>
              <h3 class="text-lg font-semibold text-gray-900">Potential Duplicate Ticket</h3>
              <p class="text-sm text-gray-600">Similar pending ticket(s) found for this customer</p>
            </div>
          </div>
        </div>

        <!-- Ticket List -->
        <div class="overflow-y-auto max-h-[400px] p-6">
          <div class="space-y-3">
            <div
              v-for="ticket in duplicateTickets"
              :key="ticket.name"
              class="border border-gray-200 rounded-lg p-4 hover:border-blue-400 hover:shadow-md transition-all cursor-pointer"
              @click="viewTicketDetails(ticket.name)"
            >
              <div class="flex items-start justify-between mb-2">
                <div class="flex items-center gap-2">
                  <span class="font-mono text-sm font-semibold text-blue-600">{{ ticket.name }}</span>
                  <span
                    class="px-2 py-0.5 text-xs font-medium rounded-full"
                    :class="getStatusClass(ticket.status)"
                  >
                    {{ ticket.status }}
                  </span>
                </div>
                <span class="text-xs text-gray-500">{{ formatDate(ticket.creation) }}</span>
              </div>
              <p class="text-sm text-gray-700 font-medium mb-2">{{ ticket.subject }}</p>
              <div class="flex items-center justify-between text-xs text-gray-500">
                <span>Priority: {{ ticket.priority || 'Medium' }}</span>
                <button
                  @click.stop="viewTicketDetails(ticket.name)"
                  class="text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1"
                >
                  View Details
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
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                    <polyline points="15 3 21 3 21 9"></polyline>
                    <line x1="10" y1="14" x2="21" y2="3"></line>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer Actions -->
        <div class="border-t border-gray-200 px-6 py-4 bg-gray-50 flex justify-end gap-3">
          <button
            @click="closeDuplicateWarning"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="proceedWithSubmission"
            class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 transition-colors"
          >
            Create New Ticket Anyway
          </button>
        </div>
      </div>
    </div>

    <!-- Ticket Details Preview Popup -->
    <div
      v-if="showTicketDetailsPopup"
      class="fixed inset-0 z-[60] flex items-center justify-center bg-black bg-opacity-50"
      @click.self="closeTicketDetails"
    >
      <div class="relative bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="bg-gray-50 border-b border-gray-200 px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div class="flex items-center gap-3">
            <button
              @click="backToDuplicateWarning"
              class="p-2 rounded-full hover:bg-gray-200 transition-colors"
              title="Back"
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
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
              </svg>
            </button>
            <div>
              <h3 class="text-lg font-semibold text-gray-900">Ticket Details</h3>
              <p class="text-sm text-gray-600">{{ selectedTicketId }}</p>
            </div>
          </div>
          <button
            @click="closeTicketDetails"
            class="p-2 rounded-full hover:bg-gray-100 transition-colors"
            title="Close"
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

        <!-- Loading State -->
        <div v-if="ticketDetailsLoading" class="flex-1 flex items-center justify-center p-8">
          <div class="text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p class="text-gray-600">Loading ticket details...</p>
          </div>
        </div>

        <!-- Error State -->
        <div v-else-if="ticketDetailsError" class="flex-1 flex items-center justify-center p-8">
          <div class="text-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="text-red-500 mx-auto mb-4"
            >
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <p class="text-red-600 font-medium mb-2">Failed to load ticket details</p>
            <p class="text-gray-600 text-sm">{{ ticketDetailsError }}</p>
          </div>
        </div>

        <!-- Ticket Details Content -->
        <div v-else-if="ticketDetails" class="flex-1 overflow-y-auto p-6">
          <!-- Ticket Header Info -->
          <div class="bg-gray-50 rounded-lg p-4 mb-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="text-xs font-semibold text-gray-500 uppercase">Ticket ID</label>
                <p class="text-sm font-mono font-semibold text-gray-900">{{ ticketDetails.name }}</p>
              </div>
              <div>
                <label class="text-xs font-semibold text-gray-500 uppercase">Status</label>
                <p>
                  <span
                    class="inline-block px-2 py-1 text-xs font-medium rounded-full"
                    :class="getStatusClass(ticketDetails.status)"
                  >
                    {{ ticketDetails.status }}
                  </span>
                </p>
              </div>
              <div>
                <label class="text-xs font-semibold text-gray-500 uppercase">Priority</label>
                <p class="text-sm text-gray-900">{{ ticketDetails.priority || 'Medium' }}</p>
              </div>
              <div>
                <label class="text-xs font-semibold text-gray-500 uppercase">Created</label>
                <p class="text-sm text-gray-900">{{ formatDate(ticketDetails.creation) }}</p>
              </div>
              <div v-if="ticketDetails.custom_customercode">
                <label class="text-xs font-semibold text-gray-500 uppercase">Customer Code</label>
                <p class="text-sm text-gray-900">{{ ticketDetails.custom_customercode }}</p>
              </div>
              <div v-if="ticketDetails.custom_customer_name">
                <label class="text-xs font-semibold text-gray-500 uppercase">Customer Name</label>
                <p class="text-sm text-gray-900">{{ ticketDetails.custom_customer_name }}</p>
              </div>
              <div v-if="ticketDetails.custom_product" class="md:col-span-2">
                <label class="text-xs font-semibold text-gray-500 uppercase">Product</label>
                <p class="text-sm text-gray-900">{{ ticketDetails.custom_product }}</p>
              </div>
            </div>
          </div>

          <!-- Subject -->
          <div class="mb-6">
            <label class="text-xs font-semibold text-gray-500 uppercase mb-2 block">Subject</label>
            <p class="text-base font-medium text-gray-900">{{ ticketDetails.subject }}</p>
          </div>

          <!-- Description -->
          <div class="mb-6">
            <label class="text-xs font-semibold text-gray-500 uppercase mb-2 block">Description</label>
            <div
              class="prose prose-sm max-w-none bg-white border border-gray-200 rounded-lg p-4"
              v-html="sanitize(ticketDetails.description || 'No description provided')"
            ></div>
          </div>

          <!-- Team & Assignee -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div v-if="ticketDetails.agent_group">
              <label class="text-xs font-semibold text-gray-500 uppercase mb-2 block">Team</label>
              <p class="text-sm text-gray-900">{{ ticketDetails.agent_group }}</p>
            </div>
            <div v-if="ticketDetails.assigned_to">
              <label class="text-xs font-semibold text-gray-500 uppercase mb-2 block">Assigned To</label>
              <p class="text-sm text-gray-900">{{ ticketDetails.assigned_to }}</p>
            </div>
          </div>

          <!-- Open Ticket Button -->
          <div class="mt-6 pt-6 border-t border-gray-200">
            <a
              :href="`/helpdesk/tickets/${ticketDetails.name}`"
              target="_blank"
              class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Open Full Ticket
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                <polyline points="15 3 21 3 21 9"></polyline>
                <line x1="10" y1="14" x2="21" y2="3"></line>
              </svg>
            </a>
          </div>
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
           
            <!-- CUSTOMER NAME FIELD WITH SEARCH -->
            <div v-else-if="field.fieldname === 'custom_customer_name'" class="relative sm:col-span-1">
              <div class="flex gap-2 items-start">
                <div class="flex-1 min-w-0">
                  <UniInput
                    :field="field"
                    :value="templateFields[field.fieldname]"
                    @change="(value) => handleOnFieldChange(value, field.fieldname, field.fieldtype)"
                    @input="(e) => safeSetField(field.fieldname, e)"
                  />
                </div>

                <!-- Customer Details Button -->
                <div class="pt-[22px]">
                  <button
                    class="inline-flex items-center gap-0.5 px-1.5 py-1 text-[10px] bg-blue-400 hover:bg-blue-500 text-white font-medium rounded transition-colors duration-200 shadow-sm whitespace-nowrap flex-shrink-0"
                    @click="openCustomerSearchPopup"
                    title="Search Customer Details"
                    type="button"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="10"
                      height="10"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    >
                      <circle cx="11" cy="11" r="8"></circle>
                      <path d="m21 21-4.35-4.35"></path>
                    </svg>
                    <span class="hidden sm:inline">Customer</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- PRODUCT FIELD WITH LICENSE BUTTON -->
            <div v-else-if="field.fieldname === 'custom_product'" class="relative sm:col-span-1">
              <div class="flex gap-2 items-start">
                <div class="flex-1 min-w-0">
                  <UniInput
                    :field="field"
                    :value="templateFields[field.fieldname]"
                    @input="(e) => safeSetField(field.fieldname, e)"
                  />
                </div>

                <!-- View License Button -->
                <div class="pt-[22px]">
                  <button
                    class="inline-flex items-center gap-0.5 px-1.5 py-1 text-[10px] bg-blue-400 hover:bg-blue-500 text-white font-medium rounded transition-colors duration-200 shadow-sm whitespace-nowrap flex-shrink-0"
                    @click="openLicensePopup"
                    title="View License Details"
                    type="button"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="10"
                      height="10"
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
                    <span class="hidden sm:inline">License</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- ALL OTHER FIELDS -->
            <UniInput
              v-else
              :field="field"
              :value="templateFields[field.fieldname]"
              @input="(e) => safeSetField(field.fieldname, e)"
            />
          </template>
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
                @click="() => handleTicketSubmit()"
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
              @click="() => handleTicketSubmit()"
            />
          </template>
        </TicketTextEditor>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { LayoutHeader, UniInput } from "@/components";
import LicenseDetailsPopup from "@/components/LicenseDetailsPopup.vue";
import CustomerSearchPopup from "@/components/CustomerSearchPopup.vue";
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

// Customer Search State
const showCustomerSearchPopup = ref(false);

// Duplicate Warning State
const showDuplicateWarning = ref(false);
const duplicateTickets = ref([]);
const pendingSubmission = ref(false);

// Ticket Details State
const showTicketDetailsPopup = ref(false);
const selectedTicketId = ref("");
const ticketDetails = ref(null);
const ticketDetailsLoading = ref(false);
const ticketDetailsError = ref("");

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

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function getStatusClass(status: string): string {
  const statusMap = {
    'Open': 'bg-yellow-100 text-yellow-800',
    'Replied': 'bg-blue-100 text-blue-800',
    'Resolved': 'bg-green-100 text-green-800',
    'Closed': 'bg-gray-100 text-gray-800',
    'Pending': 'bg-orange-100 text-orange-800',
  };
  return statusMap[status] || 'bg-gray-100 text-gray-800';
}

// ============================================
// DUPLICATE WARNING FUNCTIONS
// ============================================
function closeDuplicateWarning() {
  showDuplicateWarning.value = false;
  duplicateTickets.value = [];
  pendingSubmission.value = false;
}

function proceedWithSubmission() {
  closeDuplicateWarning();
  pendingSubmission.value = true;
  ticket.submit();
}

async function viewTicketDetails(ticketId: string) {
  selectedTicketId.value = ticketId;
  showTicketDetailsPopup.value = true;
  ticketDetailsLoading.value = true;
  ticketDetailsError.value = "";
  ticketDetails.value = null;

  try {
    const result = await call("frappe.client.get", {
      doctype: "HD Ticket",
      name: ticketId,
    });
   
    if (result) {
      ticketDetails.value = result;
    } else {
      ticketDetailsError.value = "Ticket not found";
    }
  } catch (error) {
    console.error("Error fetching ticket details:", error);
    ticketDetailsError.value = error.message || "Failed to load ticket details";
  } finally {
    ticketDetailsLoading.value = false;
  }
}

function closeTicketDetails() {
  showTicketDetailsPopup.value = false;
  selectedTicketId.value = "";
  ticketDetails.value = null;
  ticketDetailsError.value = "";
}

function backToDuplicateWarning() {
  closeTicketDetails();
  showDuplicateWarning.value = true;
}

// ============================================
// CUSTOMER SEARCH POPUP FUNCTIONS
// ============================================
function openCustomerSearchPopup() {
  showCustomerSearchPopup.value = true;
}

async function handleCustomerSelected(customer: any) {
  isManuallySelectingCustomer.value = true;
  isUpdatingInternally.value = true;
 
  safeSetField("custom_customer_name", customer.customer_name);
  safeSetField("custom_customercode", customer.custom_customercode || "");
  safeSetField("custom_product", customer.custom_productname || "");
 
  lastValidatedCustomerCode.value = customer.custom_customercode || "";
 
  await nextTick();
  isUpdatingInternally.value = false;
  isManuallySelectingCustomer.value = false;
}

// ============================================
// LICENSE POPUP HANDLERS
// ============================================
async function openLicensePopup() {
  await nextTick();

  const customerCode = extractValue(templateFields.custom_customercode)?.trim() ||
                       document.querySelector('[name="custom_customercode"]')?.value?.trim() || "";

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

  const found = await fetchCustomerName(customerCode);
  if (found) {
    lastValidatedCustomerCode.value = customerCode;
    showLicensePopup.value = true;
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

function handleLicenseLoaded(data: any) {
  licenseData.value = data;
}

// ============================================
// WATCHERS
// ============================================
watch(
  () => templateFields.custom_customer_name,
  (newName, oldName) => {
    if (isUpdatingInternally.value || isManuallySelectingCustomer.value) return;
   
    const cleanName = extractValue(newName);
   
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
// CUSTOMER CODE HANDLERS
// ============================================
function handleCustomerCodeInput(event: any) {
  const value = event.target?.value?.trim() || "";
  safeSetField("custom_customercode", value);
}

async function handleCustomerCodeEnter(event: any) {
  const enteredCode = event.target.value?.trim();
  const previousCode = lastValidatedCustomerCode.value?.trim();
  invalidCodeError.value = "";

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

  if (enteredCode === previousCode) {
    showLicensePopup.value = true;
    return;
  }

  safeSetField("custom_customercode", enteredCode);

  const found = await fetchCustomerName(enteredCode);
  if (found) {
    lastValidatedCustomerCode.value = enteredCode;
    showLicensePopup.value = true;
  } else {
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

function handleCustomerCodeBlur() {
  // Optional: Add blur handling if needed
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
// DUPLICATE TICKET CHECK
// ============================================
async function checkForDuplicates() {
  // Only check if we have customer name and subject
  if (!templateFields.custom_customer_name || !subject.value || subject.value.length < 3) {
    return true;
  }

  try {
    const result = await call("frappe.client.get_list", {
      doctype: "HD Ticket",
      filters: {
        custom_customer_name: templateFields.custom_customer_name,
        status: ["not in", ["Closed", "Resolved"]],
      },
      fields: ["name", "subject", "status", "priority", "creation"],
      order_by: "creation desc",
      limit: 10,
    });

    if (result && result.length > 0) {
      duplicateTickets.value = result;
      showDuplicateWarning.value = true;
      return false;
    }

    return true;
  } catch (error) {
    console.error("Error checking for duplicates:", error);
    return true;
  }
}

// ============================================
// TICKET CREATION WITH DUPLICATE CHECK
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

async function handleTicketSubmit() {
  // Skip duplicate check if already approved
  if (pendingSubmission.value) {
    pendingSubmission.value = false;
    return;
  }

  const shouldProceed = await checkForDuplicates();
 
  if (shouldProceed) {
    ticket.submit();
  }
}

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