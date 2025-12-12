<template>
  <div 
    v-if="show" 
    class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" 
    @click.self="$emit('update:show', false)"
  >
    <div class="relative bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-80vh overflow-hidden">
      <!-- Header -->
      <div class="bg-blue-50 border-b border-blue-200 px-6 py-4">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-900">Customer Alerts</h3>
          <button 
            @click="$emit('update:show', false)" 
            class="p-2 rounded-full hover:bg-gray-100 transition-colors" 
            title="Close"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>
      
      <!-- Content -->
      <div class="p-6 overflow-y-auto max-h-96">
        <!-- Loading State -->
        <div v-if="loading" class="flex items-center justify-center p-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        
        <!-- Empty State -->
        <div v-else-if="alerts.length === 0" class="text-center py-12 text-gray-500">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mx-auto mb-4 text-gray-400">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <p class="text-sm">No alerts found for this customer.</p>
        </div>
        
        <!-- Alerts List -->
        <div v-else class="space-y-4">
          <div 
            v-for="alert in alerts" 
            :key="alert.name" 
            class="bg-yellow-50 border border-yellow-200 rounded-lg p-4"
          >
            <p class="text-sm text-gray-900 whitespace-pre-wrap">
              {{ alert.popupmessage || 'No message' }}
            </p>
            <p v-if="alert.modified" class="text-xs text-gray-500 mt-2">
              {{ formatDate(alert.modified) }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  show: boolean;
  alerts: any[];
  loading?: boolean;
}>();

defineEmits(['update:show']);

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};
</script>
