<template>
  <Dialog :options="options">
    <template #body-main>
      <div class="flex flex-col items-center gap-4 p-6">
        <!-- Customer Name -->
        <div class="text-xl font-medium text-gray-900">
          {{ customer.doc?.name }}
        </div>

        <!-- Avatar Upload -->
        <Avatar
          size="lg"
          :label="customer.doc?.name"
          :image="customer.doc?.image"
          class="cursor-pointer hover:opacity-80"
        />
        <div class="flex gap-2">
          <FileUploader @success="(file) => updateImage(file)">
            <template #default="{ uploading, openFileSelector }">
              <Button
                :label="customer.doc?.image ? 'Change photo' : 'Upload photo'"
                :loading="uploading"
                @click="openFileSelector"
              />
            </template>
          </FileUploader>
          <Button
            v-if="customer.doc?.image"
            label="Remove photo"
            @click="updateImage(null)"
          />
        </div>

        <!-- Customer Fields -->
        <form class="w-full flex flex-col gap-4" @submit.prevent="update">
          <!-- Customer Name -->
          <Input
            v-model="formData.customer_name"
            label="Customer Name"
            type="text"
            placeholder="Tesla Inc."
            required
          />

          <!-- Customer Code (Always Editable) -->
          <Input
            v-model="formData.custom_customercode"
            label="Customer Code"
            placeholder="Enter Code"
            required
          />

          <!-- Product Name -->
          <div class="space-y-1">
            <label class="text-sm font-medium text-gray-700">Product *</label>
            <select
              v-model="formData.custom_productname"
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              required
            >
              <option value="" disabled>Select Product</option>
              <option v-for="product in products" :key="product.name" :value="product.name">
                {{ product.product }}
              </option>
            </select>
          </div>

          <!-- Address Fields -->
          <Input v-model="formData.custom_address1" label="Address Line 1" />
          <Input v-model="formData.custom_address2" label="Address Line 2" />
          <Input v-model="formData.custom_place" label="Place" />
          <Input v-model="formData.custom_district" label="District" />

          <!-- State -->
          <Input v-model="formData.custom_state" label="State" />

          <!-- Country -->
          <Input v-model="formData.custom_country" label="Country" />

          <!-- Contact Info -->
          <Input v-model="formData.custom_contactperson" label="Contact Person" />
          <Input v-model="formData.custom_phone001" label="Phone 1" />
          <Input v-model="formData.custom_phone002" label="Phone 2" />
          <Input v-model="formData.custom_email" label="Email" />

          <!-- GST No -->
          <Input v-model="formData.custom_gstno" label="GST No" />

          <!-- No of License -->
          <Input v-model="formData.custom_nooflicense" label="No of License" />

          <!-- Date of AMC Last Paid -->
          <Input
            v-model="formData.custom_dateofamclastpaid"
            label="Date of AMC Last Paid"
            type="date"
          />

          <!-- Domain -->
          <Input v-model="formData.domain" label="Domain" placeholder="example.com" />
        </form>
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import {
  Avatar,
  createDocumentResource,
  Dialog,
  FileUploader,
  toast,
  Button,
  Input,
  call,
} from "frappe-ui";
import { computed, ref, watch } from "vue";

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(["customer-updated"]);

// Resource for customer document
const customer = createDocumentResource({
  doctype: "HD Customer",
  name: props.name,
  auto: true,
  setValue: {
    onSuccess() {
      toast.success("Customer updated");
    },
    onError() {
      toast.error("Error updating customer");
    },
  },
});

// Local form data to prevent auto-save
const formData = ref({
  customer_name: "",
  custom_customercode: "",
  custom_productname: "",
  custom_address1: "",
  custom_address2: "",
  custom_place: "",
  custom_district: "",
  custom_state: "",
  custom_country: "",
  custom_contactperson: "",
  custom_phone001: "",
  custom_phone002: "",
  custom_email: "",
  custom_gstno: "",
  custom_nooflicense: "",
  custom_dateofamclastpaid: "",
  domain: "",
});

// Products list
const products = ref([]);

// Watch for customer data load and populate form
watch(
  () => customer.doc,
  (newDoc) => {
    if (newDoc) {
      formData.value = {
        customer_name: newDoc.customer_name || "",
        custom_customercode: newDoc.custom_customercode || "",
        custom_productname: newDoc.custom_productname || "",
        custom_address1: newDoc.custom_address1 || "",
        custom_address2: newDoc.custom_address2 || "",
        custom_place: newDoc.custom_place || "",
        custom_district: newDoc.custom_district || "",
        custom_state: newDoc.custom_state || "",
        custom_country: newDoc.custom_country || "",
        custom_contactperson: newDoc.custom_contactperson || "",
        custom_phone001: newDoc.custom_phone001 || "",
        custom_phone002: newDoc.custom_phone002 || "",
        custom_email: newDoc.custom_email || "",
        custom_gstno: newDoc.custom_gstno || "",
        custom_nooflicense: newDoc.custom_nooflicense || "",
        custom_dateofamclastpaid: newDoc.custom_dateofamclastpaid || "",
        domain: newDoc.domain || "",
      };
      
      // Fetch products after customer data is loaded
      fetchProducts();
    }
  },
  { immediate: true, deep: true }
);

// Fetch products
const fetchProducts = async () => {
  try {
    console.log('Fetching products...');
    const data = await call('frappe.client.get_list', {
      doctype: 'Product',
      fields: ['name', 'product', 'status', 'team'],
      limit_page_length: 999,
    });
    console.log('Products fetched:', data);
    products.value = data || [];
  } catch (error) {
    console.error('Error fetching products:', error);
    products.value = [];
  }
};

// Save and Update
const options = computed(() => ({
  title: customer.doc?.name || "Customer",
  actions: [
    {
      label: "Save",
      theme: "gray",
      variant: "solid",
      onClick: () => update(),
    },
  ],
}));

async function update() {
  try {
    await customer.setValue.submit({
      customer_name: formData.value.customer_name,
      custom_customercode: formData.value.custom_customercode,
      custom_productname: formData.value.custom_productname,
      custom_address1: formData.value.custom_address1,
      custom_address2: formData.value.custom_address2,
      custom_place: formData.value.custom_place,
      custom_district: formData.value.custom_district,
      custom_state: formData.value.custom_state,
      custom_country: formData.value.custom_country,
      custom_contactperson: formData.value.custom_contactperson,
      custom_phone001: formData.value.custom_phone001,
      custom_phone002: formData.value.custom_phone002,
      custom_email: formData.value.custom_email,
      custom_gstno: formData.value.custom_gstno,
      custom_nooflicense: formData.value.custom_nooflicense,
      custom_dateofamclastpaid: formData.value.custom_dateofamclastpaid,
      domain: formData.value.domain,
    });
    
    // Reload the customer document to get the updated data
    await customer.reload();
    
    emit("customer-updated");
  } catch (error) {
    console.error("Error updating customer:", error);
    toast.error("Failed to update customer");
  }
}

function updateImage(file) {
  customer.setValue.submit({
    image: file?.file_url || null,
  });
  emit("customer-updated");
}
</script>