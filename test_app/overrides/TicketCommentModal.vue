<template>
  <Dialog
    v-model="show"
    :options="{
      title: 'Close Ticket',
      size: 'lg',
    }"
  >
    <template #body-content>
      <div class="space-y-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Closing Comment <span class="text-red-500">*</span>
        </label>
        <textarea
          v-model="comment"
          rows="4"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg
                 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="@John could you please look into this?"
          @input="showError = false"
        ></textarea>
        <p v-if="showError" class="mt-1 text-sm text-red-600">
          Comment is required to close the ticket
        </p>
      </div>
    </template>

    <template #actions>
      <Button variant="subtle" @click="closeModal">
        Cancel
      </Button>
      <Button
        variant="solid"
        :loading="isSubmitting"
        @click="handleSubmit"
      >
        Close Ticket
      </Button>
    </template>
  </Dialog>
</template>



<script setup lang="ts">
import { ref, watch } from 'vue';
import { Dialog, Button, call } from 'frappe-ui';
import { useRouter } from 'vue-router'; 

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  ticketName: {
    type: String,
    required: true,   // HD Ticket name
  },
});

const emit = defineEmits(['update:modelValue', 'success']);

const show = ref(props.modelValue);
const comment = ref('');
const showError = ref(false);
const isSubmitting = ref(false);

const router = useRouter();

watch(
  () => props.modelValue,
  (val) => {
    show.value = val;
    if (val) {
      comment.value = '';
      showError.value = false;
      document.body.classList.add('modal-open-hide-actions');
      
      // ✅ CLEAN DEBUG - no invalid selectors
      console.log('✅ Modal opened - body class added: true');
      console.log('✅ Total buttons:', document.querySelectorAll('button').length);
      
      // ✅ Find buttons by TEXT content (JavaScript, not CSS)
      const buttonsWithClose = Array.from(document.querySelectorAll('button')).filter(btn => 
        btn.textContent?.toLowerCase().includes('close') || 
        btn.textContent?.toLowerCase().includes('new')
      );
      console.log('✅ Buttons with "Close/New":', buttonsWithClose.length);
      
    } else {
      document.body.classList.remove('modal-open-hide-actions');
      console.log('❌ Modal closed - class removed');
    }
  }
);




// ✅ MODIFY THIS WATCHER - add the if (!val) cleanup:
watch(show, (val) => {
  emit('update:modelValue', val);
  // ✅ ADD THESE LINES:
  if (!val) {
    document.body.classList.remove('modal-open-hide-actions');
  }
});

const closeModal = () => {
  show.value = false;
};

const handleSubmit = async () => {
  if (!comment.value.trim()) {
    showError.value = true;
    return;
  }

  isSubmitting.value = true;
  showError.value = false;

  try {
    // 1️⃣ SAME EVENT AS CommentTextEditor:
    // run_doc_method → HD Ticket.new_comment
    await call('run_doc_method', {
      dt: 'HD Ticket',
      dn: props.ticketName,
      method: 'new_comment',
      args: {
        content: comment.value,
        attachments: [],       // no attachments from this popup
      },
    });

    // 2️⃣ Let ActivityHeader close the ticket (status + end time)
    // ActivityHeader listens to this and runs handleCloseTicket logic.
    emit('success', comment.value.trim());

    closeModal();
    await router.push('/tickets');
  } catch (e: any) {
    console.error('Failed to add comment:', e);
    alert('Failed to add comment: ' + (e.message || 'Unknown error'));
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style>
body.modal-open-hide-actions {
  /* Debug tint */
  background: rgba(255, 0, 0, 0.05) !important;
}

/* ✅ EXACT MATCH for your Close Ticket button */
body.modal-open-hide-actions button.px-3.py-1\\.5.text-sm.font-medium.rounded-lg.bg-red-500,
body.modal-open-hide-actions button.px-3.py-1\\.5.text-sm.font-medium.rounded-lg.bg-red-600,
body.modal-open-hide-actions button:has(span:text("Close Ticket")),
body.modal-open-hide-actions button:has(span:text("Start Ticket")) {
  display: none !important;
  visibility: hidden !important;
  opacity: 0 !important;
}

/* ✅ Hide New buttons (Frappe Button component) */
body.modal-open-hide-actions button[class*="inline-flex"][class*="items-center"][class*="gap-1"] {
  display: none !important;
}

/* ✅ Hide parent container */
body.modal-open-hide-actions div[class*="flex items-center gap-2"] {
  display: none !important;
}
</style>




