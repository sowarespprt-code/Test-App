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

    <!-- Customer Alerts Popup -->
    <CustomerAlertsPopup 
      v-model:show="showAlertsPopup" :alerts="customerAlerts" 
      :loading="alertsLoading" />

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

      <!-- custom fields: aligned rows + AMC -->
      <div v-if="Boolean(visibleFields)">
        <!-- Row 1: Customer Code + Customer Name with buttons -->
        <div class="flex flex-col sm:flex-row gap-4 mb-4">
          <!-- Customer Code -->
          <div style="width: 30%; min-width: 200px;">
            <template v-for="field in visibleFields" :key="'row1_code_' + field.fieldname">
              <UniInput
                v-if="field.fieldname === 'custom_customercode'"
                :field="field"
                :value="templateFields[field.fieldname]"
                @input="handleCustomerCodeInput"
                @keydown.enter.prevent="event => handleCustomerCodeEnter(event)"
                @blur="handleCustomerCodeBlur"
              />
            </template>
          </div>

          <!-- Customer Name + buttons -->
          <div class="flex-1">
            <template v-for="field in visibleFields" :key="'row1_name_' + field.fieldname">
              <div v-if="field.fieldname === 'custom_customer_name'" class="relative">
                <div class="flex gap-2 items-start">
                  <div class="flex-1 min-w-0">
                    <UniInput
                      :field="field"
                      :value="templateFields[field.fieldname]"
                      @change="(value) => handleOnFieldChange(value, field.fieldname, field.fieldtype)"
                      @input="(e) => safeSetField(field.fieldname, e)"
                    />
                  </div>

                  <!-- Customer Search Button -->
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

                  <!-- License Button -->
                  <div class="pt-[22px]">
                    <button
                      class="inline-flex items-center gap-0.5 px-1.5 py-1 text-[10px] bg-green-500 hover:bg-green-600 text-white font-medium rounded transition-colors duration-200 shadow-sm whitespace-nowrap flex-shrink-0"
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
            </template>
          </div>
        </div>

        <!-- Row 2: Product + Phone + Contact -->
        <div class="flex flex-col sm:flex-row gap-4 mb-4">
          <!-- Product -->
          <div style="width: 30%; min-width: 200px;">
            <template v-for="field in visibleFields" :key="'prod_' + field.fieldname">
              <template v-if="field.fieldname === 'custom_product'">
                <UniInput
                  :field="field"
                  :value="templateFields[field.fieldname]"
                  @input="(e) => safeSetField(field.fieldname, e)"
                />
              </template>
            </template>
          </div>

          <!-- Phone - Clean (No special marking) -->
          <div style="width: 25%; min-width: 180px;">
            <template v-for="field in visibleFields" :key="'phone_' + field.fieldname">
              <template v-if="field.fieldname === 'custom_phone_number' || field.fieldname.toLowerCase().includes('phone')">
                <UniInput
                  :field="field"
                  :value="templateFields[field.fieldname]"
                  @input="(e) => safeSetField(field.fieldname, e)"
                />
              </template>
            </template>
          </div>


          <!-- Contact - Made wider -->
          <div style="width: 45%; min-width: 250px;">
            <template v-for="field in visibleFields" :key="'contact_' + field.fieldname">
              <template v-if="field.fieldname === 'custom_contact_person' || field.fieldname.toLowerCase().includes('contact') || field.label?.toLowerCase().includes('contact')">
                <UniInput
                  :field="field"
                  :value="templateFields[field.fieldname]"
                  @input="(e) => safeSetField(field.fieldname, e)"
                />
              </template>
            </template>
          </div>
        </div>
        <!-- Row: AMC End Date + AMC Status + Priority + Remarks (above Pop up Messages) -->
        <div class="flex flex-col sm:flex-row gap-4 mb-4">
          <!-- AMC End Date - Read-only -->
          <div class="flex flex-col" style="width: 180px; min-width: 150px;">
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              AMC End Date
            </label>
            <div
              class="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg text-sm text-gray-900 cursor-not-allowed"
            >
              {{ formattedAmcEndDate }}
            </div>
          </div>

          <!-- AMC Status - Read-only -->
          <div class="flex flex-col" style="width: 180px; min-width: 150px;">
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              AMC Status
            </label>
            <div
              class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium cursor-not-allowed"
              :class="amcStatusClass"
            >
              {{ amcStatusText }}
            </div>
          </div>


          <!-- Priority (same logic as before) -->
          <div class="flex flex-col" style="width: 180px; min-width: 150px;">
            <template
              v-for="field in visibleFields"
              :key="'priority_' + field.fieldname"
            >
              <UniInput
                v-if="field.fieldname === 'priority' || field.label === 'Priority'"
                :field="field"
                :value="templateFields[field.fieldname]"
                @change="(value) =>
                  handleOnFieldChange(value, field.fieldname, field.fieldtype)"
                @input="(e) => safeSetField(field.fieldname, e)"
              />
            </template>
          </div>

          <!-- Remarks (read-only text container as you had) -->
          <div class="flex flex-col flex-1" style="min-width: 200px;">
            <label class="block text-sm text-gray-700 mb-1">Remarks</label>
            <div
              class="px-3 py-2 bg-gray-50 border border-gray-300 rounded text-sm text-gray-900 cursor-not-allowed"
              style="min-height: 42px; max-height: 80px; overflow-y: auto;"
            >
              {{ templateFields.custom_remarks || 'No remarks available' }}
            </div>
          </div>
        </div>


        <!-- Pop up Messages - Read-only text box -->
        <div class="mb-6">
          <label class="block text-sm font-semibold text-gray-700 mb-2">Pop up Messages</label>
          <div 
            class="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg text-sm text-gray-900 cursor-not-allowed" 
            style="min-height: 100px; max-height: 150px; overflow-y: auto; white-space: pre-wrap;"
          >
            {{ popupMessagesText || 'No popup messages available' }}
          </div>
        </div>

        <!-- Remaining fields -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <template v-for="field in visibleFields" :key="'other_' + field.fieldname">
            <UniInput
              v-if="
                ![
                  'custom_customercode',
                  'custom_customer_name',
                  'custom_product',
                  'custom_contact_person',
                  'custom_phone_number',
                  'custom_remarks',
                  'custom_popupmessage',
                  'priority',
                  'custom_amc_end_date',
                  'custom_amc_status'
                ].includes(field.fieldname) &&
                !field.fieldname.toLowerCase().includes('contact') &&
                !field.fieldname.toLowerCase().includes('phone') &&
                !field.fieldname.toLowerCase().includes('priority') &&
                field.label?.toLowerCase() !== 'priority' &&
                field.label?.toLowerCase() !== 'remarks'
              "
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
import CustomerAlertsPopup from "@/components/CustomerAlertsPopup.vue";
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

const subject = ref("");
const description = ref("");
const attachments = ref<any[]>([]);
const templateFields = reactive<Record<string, any>>({});
const isFetchingCustomerName = ref(false);
const isFetchingCustomerCode = ref(false);
const isFetchingProductName = ref(false);
const showLicensePopup = ref(false);
const licenseLoading = ref(false);
const licenseError = ref("");
const licenseData = ref<any | null>(null);
const lastValidatedCustomerCode = ref("");
const MIN_CODE_LENGTH = 1;
const MINCODELENGTH = 1; 
const invalidCodeError = ref("");
const customerCode = ref("");

const showCustomerSearchPopup = ref(false);
const showAlertsPopup = ref(false);
const customerAlerts = ref<any[]>([]);
const alertsLoading = ref(false);
const popupMessagesText = ref('');


const showDuplicateWarning = ref(false);
const duplicateTickets = ref<any[]>([]);
const pendingSubmission = ref(false);

const showTicketDetailsPopup = ref(false);
const selectedTicketId = ref("");
const ticketDetails = ref<any | null>(null);
const ticketDetailsLoading = ref(false);
const ticketDetailsError = ref("");

const isUpdatingInternally = ref(false);
const isManuallySelectingCustomer = ref(false);

async function handleCustomerCodeEnter(event: any) {
  const enteredCode = event.target.value?.trim();
  const previousCode = lastValidatedCustomerCode.value?.trim();
  invalidCodeError.value = '';
  
  if (!enteredCode) {
    isUpdatingInternally.value = true;
    safeSetField('custom_customer_name', '');
    safeSetField('custom_product', '');
    safeSetField('custom_remarks', '');
    popupMessagesText.value = '';
    licenseData.value = null;
    showLicensePopup.value = false;
    showAlertsPopup.value = false;
    lastValidatedCustomerCode.value = '';
    isUpdatingInternally.value = false;
    return;
  }
  
  if (enteredCode.length < MINCODELENGTH) {
    dialog({
      title: 'Invalid Customer Code',
      message: `Customer Code must be at least ${MINCODELENGTH} characters.`,
    });
    return;
  }
  
  if (enteredCode === previousCode) {
    const customerName = templateFields.custom_customer_name;
    if (customerName) {
      await fetchCustomerRemarks(customerName);
      await fetchCustomerAlerts(customerName);
      
      // Only show alerts popup if alerts exist, NO license popup
      if (customerAlerts.value.length > 0 && popupMessagesText.value.trim()) {
        showAlertsPopup.value = true;
      }
    }
    return;
  }
  
  safeSetField('custom_customercode', enteredCode);
  const found = await fetchCustomerName(enteredCode);
  
  if (found) {
    lastValidatedCustomerCode.value = enteredCode;
    await fetchLicenseDataInBackground(enteredCode); // Keep for AMC fields only
    
    const customerName = templateFields.custom_customer_name;
    if (customerName) {
      await fetchCustomerRemarks(customerName);
      await fetchCustomerAlerts(customerName);
      
      // Only show alerts popup if alerts exist, NO license popup
      if (customerAlerts.value.length > 0 && popupMessagesText.value.trim()) {
        showAlertsPopup.value = true;
      }
    }
  } else {
    dialog({
      title: 'Invalid Customer Code',
      message: 'No customer found for this code. Please check and try again.',
    });
    
    isUpdatingInternally.value = true;
    safeSetField('custom_customer_name', '');
    safeSetField('custom_product', '');
    safeSetField('custom_remarks', '');
    popupMessagesText.value = '';
    licenseData.value = null;
    showLicensePopup.value = false;
    showAlertsPopup.value = false;
    lastValidatedCustomerCode.value = '';
    isUpdatingInternally.value = false;
  }
}

async function fetchAmcFromCustomer(customerName: string) {
  if (!customerName) return null;
  
  try {
    const result = await call("frappe.client.get_value", {
      doctype: "HD Customer",
      filters: { customer_name: customerName },
      fieldname: ["custom_dateofamclastpaid"],
    });
    
    const amcDate = result?.message?.custom_dateofamclastpaid || result?.custom_dateofamclastpaid;
    return amcDate || null;
  } catch (error) {
    console.error("Error fetching AMC date from HD Customer:", error);
    return null;
  }
}


function handleCustomerCodeBlur() {
  // optional blur logic
}

// ✅ REPLACE your existing fetchLicenseDataInBackground function with this
async function fetchLicenseDataInBackground(code: string) {
  if (!code || code.length < MIN_CODE_LENGTH) {
    licenseData.value = null;
    return;
  }
  
  licenseLoading.value = true;
  
  try {
    // Try to fetch from API first
    const result = await call("helpdesk.api.license.get_customer_license_details", {
      customer_code: code,
    });
    
    licenseData.value = result || null;
    
    // ✅ If API doesn't have AMC End Date, fetch from HD Customer
    if (!licenseData.value?.AMCEndDate || licenseData.value.AMCEndDate === "null") {
      console.log("⚠️ No AMC End Date from API, fetching from HD Customer...");
      
      const customerName = templateFields.custom_customer_name;
      if (customerName) {
        const customerAmcDate = await fetchAmcFromCustomer(customerName);
        
        if (customerAmcDate) {
          console.log("✅ Found AMC date from HD Customer:", customerAmcDate);
          
          // Create a license data object with the customer's AMC date
          licenseData.value = {
            ...licenseData.value,
            AMCEndDate: customerAmcDate,
            source: "HD Customer" // Mark the source for reference
          };
        }
      }
    } else {
      console.log("✅ Using AMC End Date from API");
      if (licenseData.value) {
        licenseData.value.source = "API";
      }
    }
  } catch (e) {
    console.error("Error fetching license data:", e);
    
    // ✅ On API error, try HD Customer as fallback
    console.log("⚠️ API error, trying HD Customer fallback...");
    const customerName = templateFields.custom_customer_name;
    
    if (customerName) {
      const customerAmcDate = await fetchAmcFromCustomer(customerName);
      
      if (customerAmcDate) {
        console.log("✅ Using AMC date from HD Customer fallback");
        licenseData.value = {
          AMCEndDate: customerAmcDate,
          source: "HD Customer"
        };
      } else {
        licenseData.value = null;
      }
    } else {
      licenseData.value = null;
    }
  } finally {
    licenseLoading.value = false;
  }
}

// ✅ REPLACE your existing formattedAmcEndDate computed with this
const formattedAmcEndDate = computed(() => {
  if (licenseLoading.value) return "Loading...";
  
  if (!licenseData.value?.AMCEndDate) return "N/A";
  
  try {
    const raw = String(licenseData.value.AMCEndDate).trim();
    
    if (!raw || raw === "null" || raw === "undefined") return "N/A";

    // Handle DD/MM/YYYY format
    if (raw.includes("/")) {
      const datePart = raw.split(" ")[0];
      const parts = datePart.split("/");
      
      if (parts.length === 3) {
        const day = parseInt(parts[0], 10);
        const month = parseInt(parts[1], 10);
        const year = parseInt(parts[2], 10);
        
        if (!isNaN(day) && !isNaN(month) && !isNaN(year)) {
          const d = new Date(year, month - 1, day);
          
          if (!isNaN(d.getTime())) {
            return d.toLocaleDateString("en-US", {
              year: "numeric",
              month: "short",
              day: "numeric",
            });
          }
        }
      }
    }

    // Handle YYYY-MM-DD format
    if (raw.includes("-")) {
      const d = new Date(raw);
      
      if (!isNaN(d.getTime())) {
        return d.toLocaleDateString("en-US", {
          year: "numeric",
          month: "short",
          day: "numeric",
        });
      }
    }

    // Try to parse as generic date
    const d = new Date(raw);
    
    if (!isNaN(d.getTime())) {
      return d.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    }

    return "Invalid Date";
  } catch (e) {
    console.error("Error parsing AMC End Date:", e);
    return "Invalid Date";
  }
});

// ✅ REPLACE your existing amcStatusText computed with this
const amcStatusText = computed(() => {
  if (licenseLoading.value) return "Loading...";
  
  if (!licenseData.value?.AMCEndDate) return "Unknown";
  
  try {
    const raw = String(licenseData.value.AMCEndDate).trim();
    
    if (!raw || raw === "null" || raw === "undefined") return "Unknown";

    let endDate: Date | undefined;

    // Handle DD/MM/YYYY format
    if (raw.includes("/")) {
      const datePart = raw.split(" ")[0];
      const parts = datePart.split("/");
      
      if (parts.length === 3) {
        const day = parseInt(parts[0], 10);
        const month = parseInt(parts[1], 10);
        const year = parseInt(parts[2], 10);
        
        if (!isNaN(day) && !isNaN(month) && !isNaN(year)) {
          endDate = new Date(year, month - 1, day);
        }
      }
    } else {
      // Handle YYYY-MM-DD or other formats
      endDate = new Date(raw);
    }

    if (!endDate || isNaN(endDate.getTime())) return "Unknown";

    // Compare with today
    const today = new Date();
    endDate.setHours(0, 0, 0, 0);
    today.setHours(0, 0, 0, 0);

    return endDate < today ? "Expired" : "Active";
  } catch (e) {
    console.error("Error calculating AMC Status:", e);
    return "Unknown";
  }
});

// ✅ Keep your existing amcStatusClass computed (no changes needed)
const amcStatusClass = computed(() => {
  if (licenseLoading.value) {
    return "bg-gray-100 text-gray-600 border border-gray-300";
  }
  
  const status = amcStatusText.value;
  
  if (status === "Expired") return "bg-red-100 text-red-800 border border-red-300";
  if (status === "Active") return "bg-green-100 text-green-800 border border-green-300";
  
  return "bg-gray-100 text-gray-800 border border-gray-300";
});

function extractValue(payload: any): string {
  if (payload == null || payload === undefined) return "";
  if (typeof payload === "string" || typeof payload === "number") {
    return String(payload).trim();
  }
  if (typeof payload === "object" && "value" in payload) {
    return String((payload as any).value || "").trim();
  }
  if (typeof payload === "object" && (payload as any).target && "value" in (payload as any).target) {
    return String((payload as any).target.value || "").trim();
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
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getStatusClass(status: string): string {
  const statusMap: Record<string, string> = {
    Open: "bg-yellow-100 text-yellow-800",
    Replied: "bg-blue-100 text-blue-800",
    Resolved: "bg-green-100 text-green-800",
    Closed: "bg-gray-100 text-gray-800",
    Pending: "bg-orange-100 text-orange-800",
  };
  return statusMap[status] || "bg-gray-100 text-gray-800";
}

function closeDuplicateWarning() {
  showDuplicateWarning.value = false;
  duplicateTickets.value = [];
  pendingSubmission.value = false;
}

async function proceedWithSubmission() {
  closeDuplicateWarning();
  pendingSubmission.value = true;

  try {
    // 1️⃣ Create / submit the ticket
    await ticket.submit();
    // At this point ticket.doc should be the saved HD Ticket

    const ticketName =
      (ticket as any).doc?.name ||
      (ticket as any).name ||
      null;

    console.log("[NEW TICKET] After submit, ticket name:", ticketName);

    if (ticketName) {
      const amcEndRaw = licenseData.value?.AMCEndDate || null;
      const amcStatus = amcStatusText.value || "Unknown";

      await call("frappe.client.set_value", {
        doctype: "HD Ticket",
        name: ticketName,
        fieldname: {
          custom_amc_end_date: amcEndRaw,
          custom_amc_status: amcStatus,

          __read_only: {
            custom_amc_end_date: 1,
            custom_amc_status: 1,
          },
        },
      });

      console.log("[NEW TICKET] AMC saved to HD Ticket:", {
        ticketName,
        custom_amc_end_date: amcEndRaw,
        custom_amc_status: amcStatus,
      });
    } else {
      console.error("[NEW TICKET] ticketName is missing after submit()");
    }

    pendingSubmission.value = false;
    // your existing navigation / toast here
  } catch (err: any) {
    console.error("[NEW TICKET] submit or set_value error:", err);
    pendingSubmission.value = false;
  }
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
  } catch (e: any) {
    console.error("Error fetching ticket details:", e);
    ticketDetailsError.value = e.message || "Failed to load ticket details";
  } finally {
    ticketDetailsLoading.value = false;
  }
}

async function fetchCustomerRemarks(customerName: string) {
  if (!customerName || customerName.trim() === "") {
    safeSetField("custom_remarks", "");
    return;
  }

  try {
    const result = await call("frappe.client.get_value", {
      doctype: "HD Customer",
      filters: { customer_name: customerName },
      fieldname: ["custom_remarks"],
    });

    const remarks = result?.message?.custom_remarks || result?.custom_remarks || "";
    safeSetField("custom_remarks", remarks);
    
  } catch (e) {
    console.error("Error fetching customer remarks:", e);
    safeSetField("custom_remarks", "");
  }
}


async function fetchCustomerAlerts(customerName: string) {
  if (!customerName?.trim()) {
    customerAlerts.value = [];
    popupMessagesText.value = '';
    showAlertsPopup.value = false;
    return;
  }
  
  alertsLoading.value = true;
  
  try {
    const customerCode = templateFields.custom_customercode || "";
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
    
    customerAlerts.value = result || [];
    
    popupMessagesText.value = customerAlerts.value
      .map(a => a.popupmessage)
      .filter(msg => msg && msg.trim())  // ✅ Filters out null, undefined, AND empty strings
      .join('\n\n') || '';

    // ✅ Only show popup if there are actual popup messages
    if (popupMessagesText.value.trim()) {
      showAlertsPopup.value = true;
    } else {
      showAlertsPopup.value = false;
    }
    
  } catch (e) {
    console.error('Error fetching customer alerts:', e);
    customerAlerts.value = [];
    popupMessagesText.value = '';
  } finally {
    alertsLoading.value = false;
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

function openCustomerSearchPopup() {
  showCustomerSearchPopup.value = true;
}

async function handleCustomerSelected(customer: any) {
  isManuallySelectingCustomer.value = true;
  isUpdatingInternally.value = true;
  
  try {
    safeSetField('custom_customer_name', customer.customer_name);
    safeSetField('custom_customercode', customer.custom_customercode);
    safeSetField('custom_product', customer.custom_productname);
    lastValidatedCustomerCode.value = customer.custom_customercode;
    
    await nextTick();
    
    // Fetch license data for AMC fields only (no popup)
    if (customer.custom_customercode) {
      await fetchLicenseDataInBackground(customer.custom_customercode);
    }
    
    await fetchCustomerRemarks(customer.customer_name);
    await fetchCustomerAlerts(customer.customer_name);
    
    // Only show alerts popup if alerts exist, NO license popup
    if (customerAlerts.value.length > 0 && popupMessagesText.value.trim()) {
      showAlertsPopup.value = true;
    }
    
  } finally {
    isUpdatingInternally.value = false;
    isManuallySelectingCustomer.value = false;
  }
}


async function openLicensePopup() {
  await nextTick();
  const code =
    extractValue(templateFields.custom_customercode)?.trim() ||
    (document.querySelector('[name="custom_customercode"]') as HTMLInputElement | null)?.value?.trim() ||
    "";
  if (!code) {
    $dialog({
      title: "Customer Code Required",
      message: "Please enter a valid Customer Code first.",
    });
    return;
  }
  if (code.length < MIN_CODE_LENGTH) {
    $dialog({
      title: "Invalid Customer Code",
      message: `Customer Code must be at least ${MIN_CODE_LENGTH} characters.`,
    });
    return;
  }
  const found = await fetchCustomerName(code);
  if (found) {
    lastValidatedCustomerCode.value = code;
    showLicensePopup.value = true;
    await fetchLicenseDataInBackground(code);
  } else {
    $dialog({
      title: "Invalid Customer Code",
      message: "No customer found for this code. Please check and try again.",
    });
    isUpdatingInternally.value = true;
    safeSetField("custom_customer_name", "");
    safeSetField("custom_product", "");
    licenseData.value = null;
    isUpdatingInternally.value = false;
    showLicensePopup.value = false;
  }
}

function handleLicenseLoaded(data: any) {
  licenseData.value = data;
}

watch(
  () => templateFields.custom_customer_name,
  (newVal, oldVal) => {
    if (isUpdatingInternally.value || isManuallySelectingCustomer.value) return;
    const clean = extractValue(newVal);
    if (!clean) {
      isUpdatingInternally.value = true;
      safeSetField("custom_customercode", "");
      safeSetField("custom_product", "");
      safeSetField("custom_remarks", "");
      safeSetField("custom_popup_messages", "");
      popupMessagesText.value = '';
      lastValidatedCustomerCode.value = "";
      licenseData.value = null;
      licenseError.value = "";
      licenseLoading.value = false;
      isUpdatingInternally.value = false;
    }
  }
);

watch(
  () => licenseData.value?.AMCEndDate,
  (newVal) => {
    if (!newVal) return;
    templateFields.custom_amc_end_date = String(newVal);
    templateFields.custom_amc_status = amcStatusText.value;
  }
);


const template = createResource({
  url: "helpdesk.helpdesk.doctype.hd_ticket_template.api.get_one",
  makeParams: () => ({ name: props.templateId || "Default" }),
  auto: true,
  onSuccess: (data: any) => {
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

function setupTemplateFields(fields: Field[]) {
  fields.forEach((field: Field) => {
    templateFields[field.fieldname] = "";
  });
  // ensure our custom display-only field exists in the reactive object
  if (!("custom_popupmessage" in templateFields)) {
    templateFields.custom_popupmessage = "";
  }
}

let oldFields: Field[] = [];

function applyFilters(fieldname: string, filters: any = null) {
  const f: Field = template.data.fields.find((ff: Field) => ff.fieldname === fieldname);
  if (!f) return;
  if (f.fieldtype === "Select") {
    handleSelectFieldUpdate(f, fieldname, filters, templateFields, oldFields);
  } else if (f.fieldtype === "Link") {
    handleLinkFieldUpdate(f, fieldname, filters, templateFields, oldFields);
  }
}

const customOnChange = computed(() => template.data?._customOnChange);

const visibleFields = computed(() => {
  const _fields = template.data?.fields?.filter(
    (f: any) => !isCustomerPortal.value || !f.hide_from_customer
  );
  return _fields?.map((f: Field) => parseField(f, templateFields)) || [];
});

function handleCustomerCodeInput(event: any) {
  const value = event.target?.value?.trim() || "";
  safeSetField("custom_customercode", value);
}

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
    }
    return false;
  } catch (e) {
    console.error("Error fetching customer:", e);
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
      filters: { customer_name: customerName },
      fieldname: ["custom_customercode"],
    });
    const code = result?.message?.custom_customercode || result?.custom_customercode;
    if (code) {
      isUpdatingInternally.value = true;
      await nextTick();
      safeSetField("custom_customercode", code);
      lastValidatedCustomerCode.value = code;
      await fetchLicenseDataInBackground(code);
      await nextTick();
      isUpdatingInternally.value = false;
    }
  } catch (e) {
    console.error("Error fetching customer code:", e);
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
      filters: { customer_name: customerName },
      fieldname: ["custom_productname"],
    });
    const product = result?.message?.custom_productname || result?.custom_productname;
    safeSetField("custom_product", product || "");
  } catch (e) {
    console.error("Error fetching product name:", e);
  } finally {
    isFetchingProductName.value = false;
  }
}

async function handleOnFieldChange(payload: any, fieldname: string, fieldtype: string) {
  if (isUpdatingInternally.value) return;
  
  const newValue = extractValue(payload);
  safeSetField(fieldname, newValue);
  
  if (fieldname === "custom_customer_name" && newValue) {
    isManuallySelectingCustomer.value = true;
    await fetchCustomerCode(newValue);
    await fetchProductName(newValue);
    await fetchCustomerRemarks(newValue);
    await fetchCustomerAlerts(newValue);
    
    // Only show alerts popup if alerts exist, NO license popup
    if (customerAlerts.value.length > 0 && popupMessagesText.value.trim()) {
      showAlertsPopup.value = true;
    }
    
    isManuallySelectingCustomer.value = false;
  }
  
  const fieldFns = customOnChange.value?.[fieldname];
  if (fieldFns) {
    fieldFns.forEach((fn: Function) => {
      try {
        fn(newValue, fieldtype);
      } catch (e) {
        console.error("Error in custom onChange:", e);
      }
    });
  }
}


async function checkForDuplicates() {
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
  } catch (e) {
    console.error("Error checking for duplicates:", e);
    return true;
  }
}

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
  validate(params: any) {
    const fields = visibleFields.value?.filter((f: any) => f.required);

    // Add phone field explicitly to required list
    const extraRequiredFields = [
      { fieldname: "subject", label: "Subject" },
      { fieldname: "description", label: "Description" },
      { fieldname: "custom_phone_number", label: "Phone Number" }, // ✅ mandatory phone
    ];

    for (const field of [...fields, ...extraRequiredFields] as any) {
      const value = params.doc[field.fieldname];
      if (isEmpty(value)) {
        return `${field.label || field.fieldname} is required`;
      }
    }
  },
  onSuccess(data: any) {
    // ✅ ADD THESE 4 LINES HERE - Store popup messages in localStorage
    if (popupMessagesText.value) {
      localStorage.setItem(`ticket_popup_${data.name}`, popupMessagesText.value);
    }
    
    // Keep existing code below
    router.push({
      name: isCustomerPortal.value ? "TicketCustomer" : "TicketAgent",
      params: { ticketId: data.name },
    });
    if (isManager) {
      updateOnboardingStep("create_first_ticket", true, false);
    }
    localStorage.setItem("firstTicket", data.name);
    if (isCustomerPortal.value) {
      capture("new_ticket_submitted", {
        data: { user: userID, ticketID: data.name, subject: subject.value },
      });
    }
  },
});

async function handleTicketSubmit() {
  if (pendingSubmission.value) {
    pendingSubmission.value = false;
    return;
  }
  const shouldProceed = await checkForDuplicates();
  if (shouldProceed) {
    ticket.submit();
  }
}

function sanitize(html: string) {
  return sanitizeHtml(html, {
    allowedTags: sanitizeHtml.defaults.allowedTags.concat(["img"]),
  });
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

