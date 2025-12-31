<template>
  <div
    v-if="modelValue"
    data-license-popup
    tabindex="-1"
    class="fixed inset-0 z-[99999] flex items-center justify-center"
    style="background-color: rgba(0, 0, 0, 0.5);"
    @mousedown.self="closePopup"
  >
    <div
      class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden"
      @mousedown.stop
    >
      <!-- Popup Header -->
      <div class="flex items-center justify-between px-5 py-3 border-b bg-gray-50">
        <h2 class="text-lg font-semibold text-gray-800">Customer License Details</h2>
        <button
          @click="closePopup"
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
        <div v-if="loading" class="flex items-center justify-center py-8">
          <div class="flex flex-col items-center gap-2">
            <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
            <p class="text-sm text-gray-600">Fetching license details...</p>
          </div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="p-3 bg-red-50 border border-red-200 rounded-lg">
          <h3 class="text-base font-medium text-red-800 mb-1">Error Loading License Details</h3>
          <p class="text-sm text-red-700">{{ error }}</p>
          <button
            @click="fetchDetails"
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

          <!-- License Type and Subscription End Date (Conditional) -->
          <div class="grid gap-4" :class="isPermanentLicense ? 'grid-cols-1' : 'grid-cols-2'">
            <div>
              <span class="text-xs font-semibold text-gray-600 uppercase tracking-wide">License Type</span>
              <p class="mt-0.5 text-sm text-gray-900">{{ licenseData.LicenseType || 'Not available' }}</p>
            </div>
            <div v-if="!isPermanentLicense">
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

          <!-- Nature of Business and License Key -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <span class="text-xs font-semibold text-gray-600 uppercase tracking-wide">Nature of Business (GST)</span>
              <p class="mt-0.5 text-sm text-gray-900">{{ licenseData.NatureOfBusiness || 'Not available' }}</p>
            </div>
            <div>
              <span class="text-xs font-semibold text-gray-600 uppercase tracking-wide">License Key</span>
              <div class="mt-0.5 flex items-center gap-2">
                <p class="text-sm text-gray-900 font-mono font-medium flex-1 break-all">
                  {{ licenseData.LicKey || 'Not available' }}
                </p>
                <button
                  v-if="licenseData.LicKey"
                  @click.stop.prevent="copyLicenseKey"
                  type="button"
                  class="px-2 py-1 text-xs font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded transition flex items-center gap-1 cursor-pointer"
                  title="Copy License Key"
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
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                  </svg>
                </button>
              </div>
            </div>
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
          @click="closePopup"
        />
        <Button
          v-if="licenseData"
          label="Refresh"
          theme="gray"
          variant="solid"
          :loading="loading"
          @click="fetchDetails"
        />
      </div>
    </div>
  </div>
</template>


<script setup lang="ts">
import { ref, watch, computed, nextTick  } from 'vue';
import { call, Button } from 'frappe-ui';

interface LicenseData {
  CustomerCode: string;
  CustomerName: string;
  OwnerName: string;
  Address1: string;
  Address2: string;
  ContactPerson: string;
  Phone1: string;
  Phone2: string;
  EmailID: string;
  NatureOfBusiness: string;
  LicenseType: string;
  LicKey: string;
  SubscriptionExpDate: string;
  SubscriptionRemarks: string;
  AMCStartDate: string;
  AMCEndDate: string;
}

interface Props {
  modelValue: boolean;
  customerCode: string;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  'update:modelValue': [value: boolean];
  'licenseLoaded': [data: LicenseData];
}>();

const loading = ref(false);
const error = ref('');
const licenseData = ref<LicenseData | null>(null);

// Computed property to check if license is permanent
const isPermanentLicense = computed(() => {
  return licenseData.value?.LicenseType?.toLowerCase() === 'permanent';
});

// Watch for popup open and customer code changes
watch(
  () => [props.modelValue, props.customerCode],
  ([isOpen, code]) => {
    if (isOpen && code) {
      fetchDetails();
    }
  },
  { immediate: true }
);

watch(() => props.modelValue, async (isOpen) => {
  if (isOpen) {
    await nextTick();
    setTimeout(() => {
      const popup = document.querySelector('[data-license-popup]') as HTMLElement;
      if (popup) {
        popup.focus();
      }
    }, 50);
  }
});

async function fetchDetails() {
  if (!props.customerCode) {
    error.value = 'Customer code is required';
    licenseData.value = null;
    return;
  }

  loading.value = true;
  error.value = '';
  licenseData.value = null;

  try {
    const data = await call('helpdesk.api.license.get_customer_license_details', {
      customer_code: props.customerCode,
    });

    if (!data) {
      throw new Error('No license details found for this customer');
    }

    licenseData.value = data;
    emit('licenseLoaded', data);
  } catch (err: any) {
    error.value = err?.message || String(err);
    licenseData.value = null;
  } finally {
    loading.value = false;
  }
}

function closePopup() {
  emit('update:modelValue', false);
}

function copyLicenseKey(event?: Event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }

  console.log('Copy function called');
  console.log('License Data:', licenseData.value);

  if (!licenseData.value?.LicKey) {
    console.error('No license key available');
    showToast('No license key to copy', 'warning');
    return;
  }

  const textToCopy = licenseData.value.LicKey;
  console.log('Copying text:', textToCopy);

  // Try fallback method first (more reliable)
  fallbackCopy(textToCopy);
}

function fallbackCopy(text: string) {
  try {
    console.log('Using fallback copy method');
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    textArea.setAttribute('readonly', '');
    document.body.appendChild(textArea);
   
    // For iOS
    if (navigator.userAgent.match(/ipad|iphone/i)) {
      const range = document.createRange();
      range.selectNodeContents(textArea);
      const selection = window.getSelection();
      if (selection) {
        selection.removeAllRanges();
        selection.addRange(range);
      }
      textArea.setSelectionRange(0, 999999);
    } else {
      textArea.select();
    }
   
    const successful = document.execCommand('copy');
    console.log('Copy command successful:', successful);
    document.body.removeChild(textArea);
   
    if (successful) {
      showToast('License key copied!', 'success');
    } else {
      // Try modern API as fallback
      tryModernClipboard(text);
    }
  } catch (err) {
    console.error('Fallback copy failed:', err);
    tryModernClipboard(text);
  }
}

function tryModernClipboard(text: string) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    console.log('Trying modern clipboard API');
    navigator.clipboard.writeText(text)
      .then(() => {
        console.log('Modern clipboard API successful');
        showToast('License key copied!', 'success');
      })
      .catch((err) => {
        console.error('Modern clipboard API failed:', err);
        showToast('Failed to copy. Please copy manually.', 'error');
      });
  } else {
    console.error('No clipboard method available');
    showToast('Copy not supported in this browser', 'error');
  }
}

function showToast(message: string, type: 'success' | 'error' | 'warning' = 'success') {
  // Using Frappe's toast notification if available
  if (typeof window !== 'undefined' && (window as any).frappe?.show_alert) {
    (window as any).frappe.show_alert({
      message: message,
      indicator: type === 'success' ? 'green' : type === 'error' ? 'red' : 'orange'
    }, 3);
  } else {
    // Fallback to alert
    alert(message);
  }
}

function formatDate(dateString: string) {
  if (!dateString) return 'Not available';
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  } catch {
    return dateString;
  }
}

function isExpired(dateString: string) {
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

function isExpiringSoon(dateString: string) {
  if (!dateString) return false;
  try {
    const date = new Date(dateString);
    const today = new Date();
    const days = Math.floor((date.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return days > 0 && days <= 30;
  } catch {
    return false;
  }
}

function getLicenseStatusClass() {
  if (!licenseData.value) return 'bg-gray-50 border border-gray-200';
 
  const amcExpired = isExpired(licenseData.value.AMCEndDate);
  const subExpired = !isPermanentLicense.value && isExpired(licenseData.value.SubscriptionExpDate);
 
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
  const subExpired = !isPermanentLicense.value && isExpired(licenseData.value.SubscriptionExpDate);
  const amcExpiringSoon = isExpiringSoon(licenseData.value.AMCEndDate);
 
  if (isPermanentLicense.value) {
    if (amcExpired) {
      return `AMC expired on ${formatDate(licenseData.value.AMCEndDate)}. Permanent license.`;
    } else if (amcExpiringSoon) {
      return `AMC is expiring soon on ${formatDate(licenseData.value.AMCEndDate)}. Permanent license.`;
    }
    return `AMC active until ${formatDate(licenseData.value.AMCEndDate)}. Permanent license.`;
  }
 
  if (amcExpired && subExpired) {
    return 'Both AMC and Subscription have expired.';
  } else if (amcExpired) {
    return `AMC expired on ${formatDate(licenseData.value.AMCEndDate)}.`;
  } else if (subExpired) {
    return `Subscription expired on ${formatDate(licenseData.value.SubscriptionExpDate)}.`;
  } else if (amcExpiringSoon) {
    return `AMC is expiring soon on ${formatDate(licenseData.value.AMCEndDate)}.`;
  }
 
  return `AMC active until ${formatDate(licenseData.value.AMCEndDate)}`;
}
</script>