<template>
  <div class="flex flex-col h-full">
    <!-- Header -->
    <div class="border-b px-5 py-4 flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">Products</h1>
      <Button variant="solid" @click="openNewProductModal">
        <template #prefix>
          <LucidePlus class="h-4 w-4" />
        </template>
        New
      </Button>
    </div>

    <!-- Product List -->
    <div class="flex-1 overflow-auto">
      <div v-if="products.length" class="border-b">
        <table class="w-full divide-y">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Product Name
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Team
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="product in products"
              :key="product.name"
              class="hover:bg-gray-50 cursor-pointer transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  {{ product.product || 'N/A' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge
                  v-if="product.status"
                  :variant="product.status === 'Enable' ? 'subtle' : 'outline'"
                  :theme="product.status === 'Enable' ? 'green' : 'gray'"
                  :label="product.status"
                />
                <span v-else class="text-sm text-gray-400">N/A</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                {{ product.team || 'N/A' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="flex h-full flex-col items-center justify-center gap-4">
        <div class="text-base text-gray-600">No products found</div>
        <Button @click="openNewProductModal">
          <template #prefix>
            <LucidePlus class="h-4 w-4" />
          </template>
          Create your first product
        </Button>
      </div>
    </div>

    <!-- New Product Modal -->
    <Dialog
      v-model="showModal"
      :options="{
        title: 'New Product',
        size: 'xl'
      }"
    >
      <template #body-content>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Product <span class="text-red-500">*</span>
            </label>
            <input
              v-model="newProduct.product"
              type="text"
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="Enter product name"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Status <span class="text-red-500">*</span>
            </label>
            <select
              v-model="newProduct.status"
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              required
            >
              <option value="" disabled>Select Status</option>
              <option value="Enable">Enable</option>
              <option value="Disable">Disable</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Team <span class="text-red-500">*</span>
            </label>
            <select
              v-model="newProduct.team"
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              required
            >
              <option value="" disabled>Select Team</option>
              <option v-for="team in teams" :key="team.name" :value="team.name">
                {{ team.name }}
              </option>
            </select>
            <div v-if="teams.length === 0" class="mt-1 text-xs text-amber-600">
              ⚠️ No teams found. Please create a team first in HD Team doctype.
            </div>
            <div v-else class="mt-1 text-xs text-green-600">
              ✅ {{ teams.length }} team(s) available
            </div>
          </div>
        </div>
      </template>

      <template #actions>
        <Button variant="subtle" @click="showModal = false">
          Cancel
        </Button>
        <Button variant="solid" :loading="isSaving" @click="saveProduct">
          Save
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { call } from 'frappe-ui';
import { Button, Dialog, Badge } from 'frappe-ui';
import LucidePlus from '~icons/lucide/plus';

export default {
  name: 'ProductList',
  components: {
    Button,
    Dialog,
    Badge,
    LucidePlus
  },
  setup() {
    const products = ref([]);
    const teams = ref([]);
    const showModal = ref(false);
    const newProduct = ref({
      product: '',
      status: '',
      team: '',
    });
    const isSaving = ref(false);

    onMounted(async () => {
      await fetchProducts();
    });

    const fetchProducts = async () => {
      try {
        const data = await call('frappe.client.get_list', {
          doctype: 'Product',
          fields: ['name', 'product', 'status', 'team'],
          limit_page_length: 999,
        });
        products.value = data || [];
        console.log('Products fetched:', data);
      } catch (error) {
        console.error('Error fetching products:', error);
      }
    };

    const fetchTeams = async () => {
      try {
        console.log('Fetching teams...');
        const data = await call('frappe.client.get_list', {
          doctype: 'HD Team',
          fields: ['name'],
          limit_page_length: 100,
        });
        console.log('Teams fetched:', data);
        teams.value = data || [];
        if (!teams.value.length) {
          console.warn('No teams found in HD Team doctype.');
        }
      } catch (error) {
        console.error('Error fetching teams:', error);
        teams.value = [];
      }
    };

    const openNewProductModal = async () => {
      newProduct.value = { product: '', status: '', team: '' };
      await fetchTeams();
      showModal.value = true;
    };

    const saveProduct = async () => {
      if (!newProduct.value.product || !newProduct.value.status || !newProduct.value.team) {
        // @ts-ignore
        frappe.msgprint('Please fill all fields.');
        return;
      }

      isSaving.value = true;
      try {
        const data = await call('frappe.client.insert', {
          doc: {
            doctype: 'Product',
            product: newProduct.value.product,
            status: newProduct.value.status,
            team: newProduct.value.team,
          },
        });
        console.log('Product saved:', data);
        showModal.value = false;
        await fetchProducts();
        // @ts-ignore
        frappe.show_alert({ message: 'Product saved successfully!', indicator: 'green' });
      } catch (error) {
        console.error('Error saving product:', error);
        // @ts-ignore
        frappe.msgprint('Failed to save product. Please try again.');
      } finally {
        isSaving.value = false;
      }
    };

    return { products, showModal, openNewProductModal, saveProduct, newProduct, isSaving, teams };
  },
};
</script>