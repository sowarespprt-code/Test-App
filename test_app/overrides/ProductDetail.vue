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
            {{ product.data?.product || productId }}
          </h1>
        </div>
        <div class="flex items-center gap-2">
          <Button variant="subtle" @click="deleteProduct" :loading="deleting">
            Delete
          </Button>
          <Button variant="solid" @click="saveProduct" :loading="saving">
            Save
          </Button>
        </div>
      </div>
    </div>

    <div v-if="product.loading" class="flex h-full items-center justify-center">
      <LoadingIndicator class="h-6 w-6 text-gray-600" />
    </div>

    <div v-else-if="product.data" class="flex-1 overflow-auto p-6">
      <div class="max-w-3xl space-y-6">
        <div class="rounded-lg border bg-white p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Product Details</h2>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Product Name <span class="text-red-500">*</span>
              </label>
              <input
                v-model="product.data.product"
                type="text"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="Enter product name"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                v-model="product.data.status"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="Enable">Enable</option>
                <option value="Disable">Disable</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Team
              </label>
              <select
                v-model="product.data.team"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="">Select team</option>
                <option v-for="team in teamList" :key="team.name" :value="team.name">
                  {{ team.name }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <div v-if="saveError" class="rounded-md bg-red-50 border border-red-200 p-4">
          <p class="text-sm text-red-800">{{ saveError }}</p>
        </div>

        <div v-if="saveSuccess" class="rounded-md bg-green-50 border border-green-200 p-4">
          <p class="text-sm text-green-800">Product saved successfully!</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import { createResource } from "frappe-ui";
import { Button, LoadingIndicator, Autocomplete } from "frappe-ui";
import LucideArrowLeft from "~icons/lucide/arrow-left";

const router = useRouter();
const route = useRoute();
const productId = route.params.productId as string;

const saving = ref(false);
const deleting = ref(false);
const saveError = ref("");
const saveSuccess = ref(false);

const product = createResource({
  url: "frappe.client.get",
  params: {
    doctype: "Product",
    name: productId,
  },
  auto: true,
});

const teamOptions = createResource({
  url: "frappe.client.get_list",
  params: {
    doctype: "HD Team",
    fields: ["name"],
    order_by: "name asc",
    limit_page_length: 999,
  },
  auto: true,
  transform: (data: any[]) => {
    return data.map((team) => ({
      label: team.name,
      value: team.name,
    }));
  },
});

async function saveProduct() {
  if (!product.data?.product || !product.data.product.trim()) {
    saveError.value = "Product name is required";
    return;
  }

  saving.value = true;
  saveError.value = "";
  saveSuccess.value = false;

  try {
    // @ts-ignore
    await frappe.call({
      method: "frappe.client.set_value",
      args: {
        doctype: "Product",
        name: productId,
        fieldname: {
          product: product.data.product,
          status: product.data.status,
          team: product.data.team || "",
        },
      },
    });

    saveSuccess.value = true;
    setTimeout(() => {
      saveSuccess.value = false;
    }, 3000);
  } catch (error: any) {
    saveError.value = error.message || "Failed to save product";
    console.error("Error saving product:", error);
  } finally {
    saving.value = false;
  }
}

async function deleteProduct() {
  // @ts-ignore
  if (!confirm("Are you sure you want to delete this product?")) {
    return;
  }

  deleting.value = true;

  try {
    // @ts-ignore
    await frappe.call({
      method: "frappe.client.delete",
      args: {
        doctype: "Product",
        name: productId,
      },
    });

    router.push({ name: "ProductList" });
  } catch (error: any) {
    saveError.value = error.message || "Failed to delete product";
    console.error("Error deleting product:", error);
  } finally {
    deleting.value = false;
  }
}
</script>