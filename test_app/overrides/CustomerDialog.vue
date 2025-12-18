<template>
  <Dialog :options="options">
    <template #body-main>
      <div class="flex flex-col items-center gap-4 p-6">
        <div class="text-xl font-medium text-gray-900">
          {{ customer.doc?.name }}
        </div>
        <Avatar
          size="lg"
          :label="customer.doc?.name"
          :image="customer.doc?.image"
          class="cursor-pointer hover:opacity-80"
        />
        <div class="flex gap-2">
          <FileUploader @success="updateImage">
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

        <form class="w-full flex flex-col gap-4" @submit.prevent="update">
          <Input
            v-model="formData.customer_name"
            label="Customer Name"
            type="text"
            placeholder="Tesla Inc."
            required
          />
          <Input
            v-model="formData.custom_customercode"
            label="Customer Code"
            placeholder="Enter Code"
            required
          />

          <!-- Product Select Field -->
          <div class="space-y-1">
            <label class="text-sm font-medium text-gray-700">Product *</label>
            <select
              v-model="formData.custom_productname"
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              required
            >
              <option value="" disabled>Select Product</option>

              <!-- Show previous product if it doesn't exist in Product doctype -->
              <option
                v-if="
                  formData.custom_productname &&
                  !products.find(p => p.name === formData.custom_productname)
                "
                :value="formData.custom_productname"
              >
                {{ formData.custom_productname }}
              </option>

              <!-- List all products -->
              <option
                v-for="product in products"
                :key="product.name"
                :value="product.name"
              >
                {{ product.product }}
              </option>
            </select>
          </div>

          <Input v-model="formData.custom_address1" label="Address Line 1" />
          <Input v-model="formData.custom_address2" label="Address Line 2" />
          <Input v-model="formData.custom_place" label="Place" />
          <Input v-model="formData.custom_district" label="District" />

          <!-- New Pincode field below District -->
          <Input v-model="formData.custom_pincode" label="Pincode" />

          <Input v-model="formData.custom_state" label="State" />
          <Input v-model="formData.custom_country" label="Country" />
          <Input v-model="formData.custom_contactperson" label="Contact Person" />
          <Input v-model="formData.custom_phone001" label="Phone 1" />
          <Input v-model="formData.custom_phone002" label="Phone 2" />
          <Input v-model="formData.custom_email" label="Email" />
          <Input v-model="formData.custom_gstno" label="GST No" />
          <Input v-model="formData.custom_nooflicense" label="No of License" />
          <Input
            v-model="formData.custom_dateofamclastpaid"
            label="Date of AMC Last Paid"
            type="date"
          />
          <Input v-model="formData.domain" label="Domain" placeholder="example.com" />

          <!-- Remarks -->
          <Input
            v-model="formData.custom_remarks"
            label="Remarks"
            type="text"
            placeholder="Enter remarks"
          />

          <!-- Status (Enabled / Disabled, mandatory, default Enabled) -->
          <div class="space-y-1">
            <label class="text-sm font-medium text-gray-700">Status *</label>
            <select
              v-model="formData.custom_status"
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              required
            >
              <option value="Enabled">Enabled</option>
              <option value="Disabled">Disabled</option>
            </select>
          </div>
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
import { computed, ref, watch, onMounted } from "vue";

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
});
const emit = defineEmits(["customer-updated"]);

const customer = createDocumentResource({
  doctype: "HD Customer",
  name: props.name,
  auto: true,
  setValue: {
    onSuccess() {
      toast.success("Customer updated");
      emit("customer-updated");
    },
    onError(error) {
      console.error("Error updating customer:", error);
      toast.error("Error updating customer");
    },
  },
});

const formData = ref({
  customer_name: "",
  custom_customercode: "",
  custom_productname: "",
  custom_address1: "",
  custom_address2: "",
  custom_place: "",
  custom_district: "",
  custom_pincode: "",             // new pincode field
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
  custom_remarks: "",
  custom_status: "Enabled",   // new status field, default Enabled
});

const products = ref([]);

const convertToYYYYMMDD = (dateStr: string) => {
  if (!dateStr) return "";
  if (dateStr.includes(" ")) dateStr = dateStr.split(" ")[0];
  if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return dateStr;
  if (/^\d{2}-\d{2}-\d{4}$/.test(dateStr)) {
    const [day, month, year] = dateStr.split("-");
    return `${year}-${month}-${day}`;
  }
  return dateStr;
};

const updateFormData = (doc: any) => {
  if (!doc) return;

  const matchedProduct = products.value.find(
    p => p.product.toLowerCase() === (doc.custom_productname || "").toLowerCase()
  );

  formData.value = {
    customer_name: doc.customer_name || "",
    custom_customercode: doc.custom_customercode || "",
    custom_productname: matchedProduct ? matchedProduct.name : (doc.custom_productname || ""),
    custom_address1: doc.custom_address1 || "",
    custom_address2: doc.custom_address2 || "",
    custom_place: doc.custom_place || "",
    custom_district: doc.custom_district || "",
    custom_pincode: doc.custom_pincode || "",
    custom_state: doc.custom_state || "",
    custom_country: doc.custom_country || "",
    custom_contactperson: doc.custom_contactperson || "",
    custom_phone001: doc.custom_phone001 || "",
    custom_phone002: doc.custom_phone002 || "",
    custom_email: doc.custom_email || "",
    custom_gstno: doc.custom_gstno || "",
    custom_nooflicense: doc.custom_nooflicense || "",
    custom_dateofamclastpaid: convertToYYYYMMDD(doc.custom_dateofamclastpaid || ""),
    domain: doc.domain || "",
    custom_remarks: doc.custom_remarks || "",
    custom_status: doc.custom_status || "Enabled",
  };
};

const fetchProducts = async () => {
  try {
    const data = await call("frappe.client.get_list", {
      doctype: "Product",
      fields: ["name", "product", "status", "team"],
      limit_page_length: 999,
    });
    products.value = Array.isArray(data) ? data : [];
  } catch (error) {
    console.error("Error fetching products:", error);
    products.value = [];
  }
};

watch(
  () => customer.doc,
  (newDoc) => {
    if (newDoc) updateFormData(newDoc);
  },
  { immediate: true }
);

onMounted(() => {
  fetchProducts();
});

const options = computed(() => ({
  title: customer.doc?.name || "Customer",
  actions: [
    {
      label: "Save",
      theme: "gray",
      variant: "solid",
      onClick: update,
    },
  ],
}));

async function update() {
  try {
    // enforce mandatory Status
    if (!formData.value.custom_status) {
      toast.error("Status is required");
      return;
    }

    const doc = customer.doc;
    Object.keys(formData.value).forEach((key) => {
      doc[key] = (formData.value as any)[key];
    });

    await call("frappe.client.save", { doc });
    await customer.reload();
    toast.success("Customer updated successfully");
    emit("customer-updated");
  } catch (error: any) {
    console.error("Error updating customer:", error);
    toast.error(error.message || "Failed to update customer");
  }
}

function updateImage(file: any) {
  customer.setValue.submit({
    image: file?.file_url || null,
  });
}
</script>

