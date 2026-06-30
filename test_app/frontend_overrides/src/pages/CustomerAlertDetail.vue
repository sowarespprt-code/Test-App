<template>
  <div class="flex flex-col h-full">
    <div class="border-b px-5 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <Button variant="ghost" @click="router.back()">
            <template #prefix>
              <LucideArrowLeft class="h-4 w-4" />
            </template>
          </Button>
          <h1 class="text-2xl font-semibold text-gray-900">
            {{ alert.data?.customer_name || alertId }}
          </h1>
        </div>
        <div class="flex items-center gap-2">
          <Button variant="subtle" @click="deleteAlert" :loading="deleting">
            Delete
          </Button>
          <Button variant="solid" @click="saveAlert" :loading="saving">
            Save
          </Button>
        </div>
      </div>
    </div>

    <div v-if="alert.loading" class="flex h-full items-center justify-center">
      <LoadingIndicator class="h-6 w-6 text-gray-600" />
    </div>

    <div v-else-if="alert.data" class="flex-1 overflow-auto p-6">
      <div class="max-w-3xl space-y-6">
        <div class="rounded-lg border bg-white p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Customer Alert Details</h2>
          
          <div class="space-y-4">
            <!-- Customer Code Field with License Button -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Customer Code <span class="text-red-500">*</span>
              </label>
              <div class="flex flex-col sm:flex-row gap-3 items-stretch sm:items-start">
                <input
                  v-model="alert.data.customer_code"
                  type="text"
                  class="w-full sm:flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  placeholder="Enter customer code"
                  readonly
                />
                <!-- License Button -->
                <button
                  class="inline-flex items-center justify-center gap-1.5 
                        px-3 py-1.5 text-xs 
                        bg-green-500 hover:bg-green-600 text-white font-medium 
                        rounded-lg transition-colors duration-200 shadow-sm 
                        whitespace-nowrap self-end sm:self-auto
                        max-w-[120px]"
                  type="button"
                  @click="openLicensePopup"
                  title="View License Details"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14"
                      viewBox="0 0 24 24" fill="none" stroke="currentColor"
                      stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                    <line x1="8" y1="21" x2="16" y2="21"></line>
                    <line x1="12" y1="17" x2="12" y2="21"></line>
                  </svg>
                  <span>License</span>
                </button>
              </div>
            </div>

            <!-- Customer Name Field -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Customer Name <span class="text-red-500">*</span>
              </label>
              <input
                v-model="alert.data.customer_name"
                type="text"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="Enter customer name"
                readonly
              />
            </div>

            <!-- Popup Message Field -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Popup Message
              </label>
              <textarea
                v-model="alert.data.popupmessage"
                rows="6"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="Enter popup message"
              />
            </div>
          </div>
        </div>

        <div v-if="saveError" class="rounded-md bg-red-50 border border-red-200 p-4">
          <p class="text-sm text-red-800">{{ saveError }}</p>
        </div>

        <div v-if="saveSuccess" class="rounded-md bg-green-50 border border-green-200 p-4">
          <p class="text-sm text-green-800">Customer alert saved successfully!</p>
        </div>
      </div>
    </div>

    <!-- License Details Popup -->
    <LicenseDetailsPopup
      v-if="showLicensePopup"
      v-model="showLicensePopup"
      :customer-code="alert.data?.customer_code || ''"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { createResource, call } from "frappe-ui";
import { Button, LoadingIndicator } from "frappe-ui";
import LucideArrowLeft from "~icons/lucide/arrow-left";
import LicenseDetailsPopup from "@/components/LicenseDetailsPopup.vue";

const router = useRouter();
const route = useRoute();
const alertId = route.params.alertId as string;

const saving = ref(false);
const deleting = ref(false);
const saveError = ref("");
const saveSuccess = ref(false);
const showLicensePopup = ref(false);

// Load Customer Alert data with customer_code and popupmessage
const alert = createResource({
  url: "frappe.client.get",
  params: {
    doctype: "Customer Alert",
    name: alertId,
  },
  auto: true,
});

onMounted(async () => {
  // No teams needed for Customer Alert
});

function openLicensePopup() {
  if (!alert.data?.customer_code) {
    saveError.value = "Customer code is required to view license details";
    setTimeout(() => {
      saveError.value = "";
    }, 3000);
    return;
  }
  showLicensePopup.value = true;
}

async function saveAlert() {
  if (!alert.data?.customer_code || !alert.data.customer_code.trim()) {
    saveError.value = "Customer code is required";
    return;
  }
  if (!alert.data?.customer_name || !alert.data.customer_name.trim()) {
    saveError.value = "Customer name is required";
    return;
  }

  saving.value = true;
  saveError.value = "";
  saveSuccess.value = false;

  try {
    await call("frappe.client.set_value", {
      doctype: "Customer Alert",
      name: alertId,
      fieldname: {
        customer_code: alert.data.customer_code,
        customer_name: alert.data.customer_name,
        popupmessage: alert.data.popupmessage || "",
      },
    });

    saveSuccess.value = true;
    setTimeout(() => {
      saveSuccess.value = false;
    }, 3000);
  } catch (error: any) {
    saveError.value = error.message || "Failed to save customer alert";
    console.error("Error saving customer alert:", error);
  } finally {
    saving.value = false;
  }
}

async function deleteAlert() {
  if (!confirm("Are you sure you want to delete this customer alert?")) {
    return;
  }

  deleting.value = true;

  try {
    await call("frappe.client.delete", {
      doctype: "Customer Alert",
      name: alertId,
    });

    router.push({ name: "CustomerAlertList" });
  } catch (error: any) {
    saveError.value = error.message || "Failed to delete customer alert";
    console.error("Error deleting customer alert:", error);
  } finally {
    deleting.value = false;
  }
}
</script>
