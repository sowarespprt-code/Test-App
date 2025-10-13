<template>
  <div>
    <Dialog
      v-model="model"
      :options="{ title: 'Add New Customer', size: 'lg' }"
    >
      <template #body-content>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <!-- Customer Name -->
            <div class="space-y-1">
              <Input
                v-model="state.customer_name"
                label="Customer Name"
                type="text"
                placeholder="Tesla Inc."
              />
            </div>
            
            <!-- Customer Code (Mandatory, Unique) -->
            <div class="space-y-1">
              <Input
                v-model="state.custom_customercode"
                label="Customer Code *"
                type="text"
                placeholder="CUST001"
              />
            </div>
            
            <!-- Product Name (Mandatory) -->
            <div class="space-y-1">
              <Input
                v-model="state.custom_productname"
                label="Product Name *"
                type="text"
                placeholder="Product Name"
              />
            </div>
            
            <!-- Domain -->
            <div class="space-y-1">
              <Input
                v-model="state.domain"
                label="Domain"
                type="text"
                placeholder="eg: tesla.com, mycompany.com"
              />
            </div>
            
            <!-- Address 1 -->
            <div class="space-y-1 col-span-2">
              <Input
                v-model="state.custom_address1"
                label="Address 1"
                type="textarea"
                placeholder="Address Line 1"
              />
            </div>
            
            <!-- Address 2 -->
            <div class="space-y-1 col-span-2">
              <Input
                v-model="state.custom_address2"
                label="Address 2"
                type="textarea"
                placeholder="Address Line 2"
              />
            </div>
            
            <!-- Place -->
            <div class="space-y-1">
              <Input
                v-model="state.custom_place"
                label="Place"
                type="text"
                placeholder="Place"
              />
            </div>
            
            <!-- District -->
            <div class="space-y-1">
              <Input
                v-model="state.custom_district"
                label="District"
                type="text"
                placeholder="District"
              />
            </div>
            
            <!-- Contact Person -->
            <div class="space-y-1">
              <Input
                v-model="state.custom_contactperson"
                label="Contact Person"
                type="text"
                placeholder="Contact Person Name"
              />
            </div>
            
            <!-- Phone 1 -->
            <div class="space-y-1">
              <Input
                v-model="state.custom_phone001"
                label="Phone 1"
                type="text"
                placeholder="Phone Number"
              />
            </div>
            
            <!-- Phone 2 -->
            <div class="space-y-1">
              <Input
                v-model="state.custom_phone002"
                label="Phone 2"
                type="text"
                placeholder="Alternate Phone"
              />
            </div>
            
            <!-- Email -->
            <div class="space-y-1">
              <Input
                v-model="state.custom_email"
                label="Email"
                type="email"
                placeholder="email@example.com"
              />
            </div>
          </div>
          
          <div class="float-right flex space-x-2">
            <Button
              label="Cancel"
              theme="gray"
              variant="subtle"
              @click="model = false"
            />
            <Button
              label="Add"
              theme="gray"
              variant="solid"
              @click.prevent="addCustomer"
            />
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { Dialog, Input, createResource, toast } from "frappe-ui";
import { reactive } from "vue";

const emit = defineEmits(["customerCreated"]);
const model = defineModel<boolean>();

const state = reactive({
  customer_name: "",
  domain: "",
  custom_customercode: "",
  custom_productname: "",
  custom_address1: "",
  custom_address2: "",
  custom_place: "",
  custom_district: "",
  custom_contactperson: "",
  custom_phone001: "",
  custom_phone002: "",
  custom_email: "",
});

const customerResource = createResource({
  url: "frappe.client.insert",
  method: "POST",
  onSuccess: () => {
    // Reset form
    state.customer_name = "";
    state.domain = "";
    state.custom_customercode = "";
    state.custom_productname = "";
    state.custom_address1 = "";
    state.custom_address2 = "";
    state.custom_place = "";
    state.custom_district = "";
    state.custom_contactperson = "";
    state.custom_phone001 = "";
    state.custom_phone002 = "";
    state.custom_email = "";
    
    toast.success("Customer created");
    emit("customerCreated");
  },
  onError: (err) => {
    toast.error(err.messages?.[0] || "Failed to create customer");
  },
});

function addCustomer() {
  // Validation
  if (!state.customer_name) {
    toast.error("Customer name is required");
    return;
  }
  if (!state.custom_customercode) {
    toast.error("Customer code is required");
    return;
  }
  if (!state.custom_productname) {
    toast.error("Product name is required");
    return;
  }
  
  customerResource.submit({
    doc: {
      doctype: "HD Customer",
      customer_name: state.customer_name,
      domain: state.domain,
      custom_customercode: state.custom_customercode,
      custom_productname: state.custom_productname,
      custom_address1: state.custom_address1,
      custom_address2: state.custom_address2,
      custom_place: state.custom_place,
      custom_district: state.custom_district,
      custom_contactperson: state.custom_contactperson,
      custom_phone001: state.custom_phone001,
      custom_phone002: state.custom_phone002,
      custom_email: state.custom_email,
    },
  });
}
</script>