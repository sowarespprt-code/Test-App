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
              <label class="text-sm font-medium text-gray-700">Product *</label>
              <Autocomplete
                v-model="state.custom_productname"
                :options="productOptions.data || []"
                placeholder="Select Product..."
                class="w-full"
                @search="handleProductSearch"
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
            
            <!-- Address 1 (Text type) -->
            <div class="space-y-1 col-span-2">
              <Input
                v-model="state.custom_address1"
                label="Address 1"
                type="textarea"
                placeholder="Address Line 1"
              />
            </div>
            
            <!-- Address 2 (Small Text type) -->
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
            
            <!-- State -->
            <div class="space-y-1">
              <Input
                v-model="state.custom_state"
                label="State"
                type="text"
                placeholder="State"
              />
            </div>
            
            <!-- Country -->
            <div class="space-y-1">
              <Input
                v-model="state.custom_country"
                label="Country"
                type="text"
                placeholder="Country"
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
                label="Phone1"
                type="text"
                placeholder="Phone Number"
              />
            </div>
            
            <!-- Phone 2 -->
            <div class="space-y-1">
              <Input
                v-model="state.custom_phone002"
                label="Phone2"
                type="text"
                placeholder="Alternate Phone"
              />
            </div>
            
            <!-- GST No -->
            <div class="space-y-1">
              <Input
                v-model="state.custom_gstno"
                label="GST No"
                type="text"
                placeholder="GST Number"
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
            
            <!-- No of License -->
            <div class="space-y-1">
              <Input
                v-model="state.custom_nooflicense"
                label="No of License"
                type="text"
                placeholder="Number of Licenses"
              />
            </div>
            
            <!-- Date of AMC Last Paid -->
            <div class="space-y-1">
              <Input
                v-model="state.custom_dateofamclastpaid"
                label="Date of AMC Last Paid"
                type="date"
                placeholder="Select Date"
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
import { Dialog, Input, Autocomplete, createResource, toast } from "frappe-ui";
import { reactive, ref } from "vue";

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
  custom_state: "",
  custom_country: "",
  custom_contactperson: "",
  custom_phone001: "",
  custom_phone002: "",
  custom_gstno: "",
  custom_email: "",
  custom_nooflicense: "",
  custom_dateofamclastpaid: "",
});

// Create a resource for fetching products with proper error handling
const productOptions = createResource({
  url: "frappe.client.get_list",
  params: {
    doctype: "Product",
    fields: ["name", "product", "status", "team"],
    order_by: "product asc",
    limit_page_length: 999,
  },
  auto: true,
  transform: (data: any[]) => {
    if (!data || !Array.isArray(data)) {
      return [];
    }
    return data.map((item) => ({
      label: item.product || item.name,
      value: item.name,
    }));
  },
  onError: (error) => {
    console.error("Error fetching products:", error);
    return [];
  },
});

// Handle product search with debouncing
let searchTimeout = null;
function handleProductSearch(query) {
  if (searchTimeout) {
    clearTimeout(searchTimeout);
  }

  searchTimeout = setTimeout(() => {
    const params = {
      doctype: "Product",
      fields: ["name", "product", "status", "team"],
      order_by: "product asc",
      limit_page_length: 999,
    };

    if (query) {
      params.filters = [["product", "like", `%${query}%`]];
    }

    productOptions.update({ params });
    productOptions.fetch();
  }, 300);
}

const customerResource = createResource({
  url: "frappe.client.insert",
  method: "POST",
  onSuccess: () => {
    state.customer_name = "";
    state.domain = "";
    state.custom_customercode = "";
    state.custom_productname = "";
    state.custom_address1 = "";
    state.custom_address2 = "";
    state.custom_place = "";
    state.custom_district = "";
    state.custom_state = "";
    state.custom_country = "";
    state.custom_contactperson = "";
    state.custom_phone001 = "";
    state.custom_phone002 = "";
    state.custom_gstno = "";
    state.custom_email = "";
    state.custom_nooflicense = "";
    state.custom_dateofamclastpaid = "";

    productOptions.data = [];

    toast.success("Customer created");
    emit("customerCreated");
    model.value = false;
  },
  onError: (err) => {
    toast.error(err.messages?.[0] || "Failed to create customer");
  },
});

function addCustomer() {
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

  // Extract the value from the Autocomplete object
  const productValue = typeof state.custom_productname === 'object' 
    ? state.custom_productname.value 
    : state.custom_productname;

  customerResource.submit({
    doc: {
      doctype: "HD Customer",
      customer_name: state.customer_name,
      domain: state.domain,
      custom_customercode: state.custom_customercode,
      custom_productname: productValue,
      custom_address1: state.custom_address1,
      custom_address2: state.custom_address2,
      custom_place: state.custom_place,
      custom_district: state.custom_district,
      custom_state: state.custom_state,
      custom_country: state.custom_country,
      custom_contactperson: state.custom_contactperson,
      custom_phone001: state.custom_phone001,
      custom_phone002: state.custom_phone002,
      custom_gstno: state.custom_gstno,
      custom_email: state.custom_email,
      custom_nooflicense: state.custom_nooflicense,
      custom_dateofamclastpaid: state.custom_dateofamclastpaid,
    },
  });
}
</script>