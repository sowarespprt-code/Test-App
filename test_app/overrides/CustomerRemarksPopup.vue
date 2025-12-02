<template>
  <div
    v-if="modelValue"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
    @click.self="close"
  >
    <div class="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between px-5 py-3 border-b bg-gray-50">
        <h2 class="text-lg font-semibold text-gray-800">
          Customer Remarks
        </h2>
        <button
          @click="close"
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

      <!-- Body -->
      <div class="px-5 py-4">
        <label class="block text-xs font-semibold text-gray-500 uppercase mb-2">
          Remarks from Customer Alert
        </label>
        <textarea
          class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm bg-gray-50 text-gray-800"
          rows="6"
          :value="remarks"
          readonly
        />
      </div>

      <!-- Footer -->
      <div class="flex justify-end px-5 py-3 border-t bg-gray-50">
        <Button label="Close" theme="gray" variant="subtle" @click="close" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Button } from "frappe-ui";

interface Props {
  modelValue: boolean;
  remarks: string;
}
interface Emits {
  (e: "update:modelValue", value: boolean): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

function close() {
  emit("update:modelValue", false);
}
</script>
