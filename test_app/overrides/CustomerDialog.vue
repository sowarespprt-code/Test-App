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

          <!-- Fixed Customer Code -->
          <Input
            v-model="custom_customercode"
            label="Customer Code"
            placeholder="Enter Code"
            :disabled="customerCodeFixed"
            required
          />

          <!-- Product Name -->
          <Input
            v-model="custom_productname"
            label="Product Name"
            placeholder="Enter Product Name"
            required
          />

          <!-- Address Fields -->
          <Input v-model="custom_address1" label="Address Line 1" />
          <Input v-model="custom_address2" label="Address Line 2" />
          <Input v-model="custom_place" label="Place" />
          <Input v-model="custom_district" label="District" />

          <!-- Contact Info -->
          <Input v-model="custom_contactperson" label="Contact Person" />
          <Input v-model="custom_phone001" label="Phone 1" />
          <Input v-model="custom_phone002" label="Phone 2" />
          <Input v-model="custom_email" label="Email" />

          <!-- Domain -->
          <Input v-model="domain" label="Domain" placeholder="example.com" />

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
} from "frappe-ui";
import { computed, ref, onMounted } from "vue";

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
    },
    onError() {
      toast.error("Error updating customer");
    },
  },
});

// Computed properties for each field
const domain = computed({
  get() {
    return customer.doc?.domain;
  },
  set(d) {
    customer.doc.domain = d;
  },
});

const custom_customercode = computed({
  get() {
    return customer.doc?.custom_customercode;
  },
  set(v) {
    customer.doc.custom_customercode = v;
  },
});
const custom_productname = computed({
  get() {
    return customer.doc?.custom_productname;
  },
  set(v) {
    customer.doc.custom_productname = v;
  },
});
const custom_address1 = computed({
  get() {
    return customer.doc?.custom_address1;
  },
  set(v) {
    customer.doc.custom_address1 = v;
  },
});
const custom_address2 = computed({
  get() {
    return customer.doc?.custom_address2;
  },
  set(v) {
    customer.doc.custom_address2 = v;
  },
});
const custom_place = computed({
  get() {
    return customer.doc?.custom_place;
  },
  set(v) {
    customer.doc.custom_place = v;
  },
});
const custom_district = computed({
  get() {
    return customer.doc?.custom_district;
  },
  set(v) {
    customer.doc.custom_district = v;
  },
});
const custom_contactperson = computed({
  get() {
    return customer.doc?.custom_contactperson;
  },
  set(v) {
    customer.doc.custom_contactperson = v;
  },
});
const custom_phone001 = computed({
  get() {
    return customer.doc?.custom_phone001;
  },
  set(v) {
    customer.doc.custom_phone001 = v;
  },
});
const custom_phone002 = computed({
  get() {
    return customer.doc?.custom_phone002;
  },
  set(v) {
    customer.doc.custom_phone002 = v;
  },
});
const custom_email = computed({
  get() {
    return customer.doc?.custom_email;
  },
  set(v) {
    customer.doc.custom_email = v;
  },
});

// Disable customer code if already exists
const customerCodeFixed = ref(false);

onMounted(() => {
  if (customer.doc?.custom_customercode) {
    customerCodeFixed.value = true;
  }
});

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
  await customer.setValue.submit({
    custom_customercode: custom_customercode.value,
    custom_productname: custom_productname.value,
    custom_address1: custom_address1.value,
    custom_address2: custom_address2.value,
    custom_place: custom_place.value,
    custom_district: custom_district.value,
    custom_contactperson: custom_contactperson.value,
    custom_phone001: custom_phone001.value,
    custom_phone002: custom_phone002.value,
    custom_email: custom_email.value,
    domain: domain.value,
  });
  emit("customer-updated");
}

function updateImage(file) {
  customer.setValue.submit({
    image: file?.file_url || null,
  });
  emit("customer-updated");
}
</script>
