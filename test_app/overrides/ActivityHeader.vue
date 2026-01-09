<template>
  <div
    class="md:mx-10 md:my-4 flex items-center justify-between text-lg font-medium mx-6 mb-4 !mt-8"
    v-show="!showAssignmentPopup"
  >
    <!-- LEFT: labels + times + LOCATION -->
    <div class="flex flex-col gap-2">
      <div class="flex items-center text-xl font-semibold text-gray-800 gap-4">
        <span>{{ title }}</span>
        <div v-if="title === 'Activity'" class="flex items-center gap-6 text-xs text-gray-500 mb-1">
          <span v-if="startTimeDisplay">
            <span class="font-semibold">Start:</span> {{ formatTime(startTimeDisplay) }}
          </span>
          <span v-if="endTimeDisplay">
            <span class="font-semibold">End:</span> {{ formatTime(endTimeDisplay) }}
          </span>
        </div>
      </div>
      
      <!-- Clickable location display -->
      <div v-if="title === 'Activity' && locationText" 
          @click="showLocationModal = true"
          class="flex items-center gap-2 text-xs bg-gradient-to-r from-blue-50 to-indigo-50 
                  border border-blue-100 px-4 py-2 rounded-xl shadow-sm max-w-md cursor-pointer 
                  hover:shadow-md hover:border-blue-200 transition-all duration-200">
        <span class="text-lg">📍</span>
        <span class="font-medium text-gray-800 truncate">{{ locationText }}</span>
        <span class="text-blue-500 text-xs ml-auto">View Map</span>
      </div>
    </div>


    <!-- RIGHT: buttons -->
    <div class="flex items-center gap-2" style="position: relative; z-index: 10;">
      <!-- Start / Close Ticket button -->
      <button
        v-if="showStartClose && title === 'Activity'"
        :disabled="isUpdating"
        :class="[
          'px-3 py-1.5 text-sm font-medium rounded-lg transition-colors duration-200',
          'focus:outline-none focus:ring-2 focus:ring-offset-1 touch-manipulation',
          isUpdating 
            ? 'bg-gray-400 text-white cursor-not-allowed' 
            : buttonState.isClose 
              ? 'bg-red-500 hover:bg-red-600 text-white focus:ring-red-500'
              : 'bg-green-500 hover:bg-green-600 text-white focus:ring-green-500'
        ]"
        @click.stop="handleButtonClick"
      >
        <span v-if="isUpdating" class="flex items-center gap-2">
          <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          {{ buttonInfo?.is_close ? 'Closing...' : 'Starting...' }}
        </span>
        <span v-else>{{ buttonState.text || buttonInfo?.button_text || 'Start Ticket' }}</span>
      </button>

      <div v-if="isStatusRefreshing" 
          class="absolute inset-0 bg-black bg-opacity-20 flex items-center justify-center rounded-lg z-10"
          style="pointer-events: none;">
        <div class="bg-white p-3 rounded-full shadow-lg animate-spin">
          <svg class="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" pathLength="1" class="opacity-25"/>
            <path d="M4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4Z" stroke="currentColor" stroke-width="3" pathLength="1" class="opacity-75"/>
          </svg>
        </div>
      </div>


      <!-- ✅ MOBILE-FRIENDLY: Assigned to message -->
      <div 
        v-else-if="!showStartClose && buttonInfo.button_text && title === 'Activity'"
        class="px-3 py-2 sm:px-4 sm:py-2.5 bg-gradient-to-r from-amber-50 to-yellow-50 border-2 border-amber-300 rounded-lg text-xs sm:text-sm font-semibold text-amber-900 flex items-center justify-center gap-2 shadow-sm"
      >
        <svg class="w-4 h-4 sm:w-5 sm:h-5 text-amber-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
        </svg>
        <span class="truncate">{{ buttonInfo.button_text }}</span>
      </div>


      <Button
        v-if="title == 'Emails'"
        variant="solid"
        @click="communicationAreaRef?.toggleEmailBox() ?? toggleEmailBox()"
      >
        <template #prefix>
          <FeatherIcon name="plus" class="h-4 w-4" />
        </template>
        <span>New Email</span>
      </Button>

      <Button
        v-else-if="title == 'Comments'"
        variant="solid"
        @click="communicationAreaRef?.toggleCommentBox() ?? toggleCommentBox()"
      >
        <template #prefix>
          <FeatherIcon name="plus" class="h-4 w-4" />
        </template>
        <span>New Comment</span>
      </Button>

      <Dropdown v-else-if="title == 'Calls'" :options="callActions" @click.stop>
        <template #default="{ open }">
          <Button variant="solid" class="flex items-center gap-1">
            <template #prefix>
              <FeatherIcon name="plus" class="h-4 w-4" />
            </template>
            <span>New</span>
            <template #suffix>
              <FeatherIcon
                :name="open ? 'chevron-up' : 'chevron-down'"
                class="h-4 w-4"
              />
            </template>
          </Button>
        </template>
      </Dropdown>

      <Dropdown v-else :options="defaultActions" @click.stop>
        <template #default="{ open }">
          <Button variant="solid" class="flex items-center gap-1">
            <template #prefix>
              <FeatherIcon name="plus" class="h-4 w-4" />
            </template>
            <span>New</span>
            <template #suffix>
              <FeatherIcon
                :name="open ? 'chevron-up' : 'chevron-down'"
                class="h-4 w-4"
              />
            </template>
          </Button>
        </template>
      </Dropdown>
    </div>
  </div>

  <CallLogModal
    v-model="showCallLogModal"
    :ticketId="ticketId"
    @after-insert="refreshTicket"
  />

  <!-- ✅ Close Ticket Modal -->
  <TicketCommentModal
    v-model="showCloseModal"
    :ticket-name="props.ticketName"
    @success="onCloseWithComment"
  />

  <!-- Mobile-Responsive Agent Map Modal -->
  <div 
    v-if="showLocationModal"
    class="fixed inset-0 z-[9999] bg-black bg-opacity-50 flex items-center justify-center p-2 sm:p-4"
    @click.self="showLocationModal = false"
    @keydown.esc="showLocationModal = false"
  >
    <!-- Map Container - Responsive sizing -->
    <div class="bg-white rounded-2xl shadow-2xl w-full h-full sm:h-auto sm:max-w-4xl sm:max-h-[90vh] flex flex-col overflow-hidden">
      
      <!-- Header - Compact on mobile -->
      <div class="flex items-center justify-between p-3 sm:p-6 border-b border-gray-100">
        <div class="flex-1 min-w-0">
          <h2 class="text-lg sm:text-2xl font-bold text-gray-900">Agent Location</h2>
          <p v-if="locationText" class="text-xs sm:text-sm text-gray-500 mt-1 truncate">
            {{ locationText }}
          </p>
        </div>
        <button 
          @click="showLocationModal = false"
          class="p-2 sm:p-3 text-gray-400 hover:text-gray-900 hover:bg-gray-100 rounded-xl transition-all ml-2 sm:ml-4 flex-shrink-0"
          title="Close">
          <svg class="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
      
      <!-- Map - Full height on mobile, constrained on desktop -->
      <div ref="mapContainer" class="flex-1 w-full min-h-[400px] sm:min-h-[500px]"></div>
    </div>
  </div>

  <!-- ✅ ADD THIS NEW DIALOG (at very end) -->
  <Dialog
    v-model="showAssignmentPopup"
    :options="{
      title: 'Ticket Already Assigned',
      size: 'md',
    }"
  >
    <template #body-content>
      <div class="space-y-4 py-4">
        <div class="flex items-start gap-4">
          <div class="flex-shrink-0 w-14 h-14 bg-yellow-100 rounded-full flex items-center justify-center">
            <svg class="w-7 h-7 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
            </svg>
          </div>
          <div class="flex-1">
            <p class="text-lg font-semibold text-gray-900 mb-3">
              {{ assignmentAlert.message }}
            </p>
            <p class="text-sm text-gray-600 leading-relaxed">
              This ticket is currently being handled by <span class="font-semibold text-gray-800">{{ assignmentAlert.assignee }}</span>. 
            </p>
          </div>
        </div>
      </div>
    </template>

    <template #actions>
      <Button variant="solid" @click="closeAssignmentPopup">
        OK, Got It
      </Button>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { CommentIcon, EmailIcon, PhoneIcon } from "@/components/icons";
import CallLogModal from "@/pages/call-logs/CallLogModal.vue";
import TicketCommentModal from "@/components/ticket/TicketCommentModal.vue";
import { useTelephonyStore } from "@/stores/telephony";
import { toggleCommentBox, toggleEmailBox } from "@/pages/ticket/modalStates";
import { Dropdown, Button, call, Dialog } from "frappe-ui";
import { storeToRefs } from "pinia";
import { ActivitiesSymbol } from "@/types";
import { computed, h, inject, ref, Ref, watch, onMounted, nextTick } from "vue";
import "leaflet/dist/leaflet.css";
import L from "leaflet";


const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  ticketName: {
    type: String,
    required: false,
    default: "",
  },
  ticketStatus: {
    type: String,
    required: false,
    default: "",
  },
  customStartTime: {
    type: String,
    required: false,
    default: "",
  },
  customEndTime: {
    type: String,
    required: false,
    default: "",
  }
});

const communicationAreaRef: Ref = inject("communicationArea");
const makeCall = inject<() => void>("makeCall");
const refreshTicket = inject<() => void>("refreshTicket");
const showCallLogModal = ref(false);
const showCloseModal = ref(false);
const { isCallingEnabled } = storeToRefs(useTelephonyStore());
const ticketId = inject<string>("ticketId");

const isTicketStarted = ref(false);
const isUpdating = ref(false);

const fetchedStartTime = ref("");
const fetchedEndTime = ref("");
const fetchedLocationText = ref("");

const showLocationModal = ref(false);
const mapContainer = ref(null);
const mapInstance = ref(null);
const savedLatitude = ref(null);
const savedLongitude = ref(null);
const fetchedAssignedTo = ref("");
const isAdminRole = ref(false);
const isAssignee = ref(false);
const currentUser = inject('user'); 
const buttonInfo = ref({});
const showStartClose = ref(true);
const buttonState = ref({ show: true, text: 'Start Ticket', isClose: false });
const isStatusRefreshing = ref(false);

const assignmentAlert = ref({ show_alert: 0, message: '', assignee: '' });
const showAssignmentPopup = ref(false); 


const locationText = computed(() => {
  return fetchedLocationText.value || '';
});

const closeAssignmentPopup = () => {
  showAssignmentPopup.value = false;
};

const fetchTicketTimes = async () => {
  if (!props.ticketName) return;

  try {
    // 1. ✅ Check alert FIRST
    const alertRes = await call("test_app.api1.get_ticket_assignment_alert", {
      ticket_name: props.ticketName
    });
    
    console.log("🔔 ALERT RESPONSE:", alertRes);
    
    // ✅ FIX: alertRes IS the object, not alertRes.message
    if (alertRes?.show_alert === 1) {
      assignmentAlert.value = {
        show_alert: alertRes.show_alert,
        message: alertRes.message,
        assignee: alertRes.assignee
      };
      
      // Show popup immediately
      await nextTick();
      showAssignmentPopup.value = true;
      console.log("✅ POPUP TRIGGERED:", showAssignmentPopup.value);
    }
  } catch (alertError) {
    console.warn("⚠️ Assignment alert fetch failed:", alertError);
  }
  
  try {
    // Backend API
    const btnResponse = await call("test_app.api1.get_ticket_button_visibility", {
      ticket_name: props.ticketName
    });
    
    console.log("Backend response:", btnResponse);
    
    buttonState.value = {
      show: !!btnResponse.show_button,
      text: btnResponse.button_text || 'Start Ticket',
      isClose: !!btnResponse.is_close  // 0 → false (green), 1 → true (red)
    };
    buttonInfo.value = btnResponse;
    showStartClose.value = buttonState.value.show;

    // Existing fields
    const ticketDoc = await call("frappe.client.get", {
      doctype: "HD Ticket",
      name: props.ticketName
    });
    
    fetchedStartTime.value = ticketDoc.custom_start_time || "";
    fetchedEndTime.value = ticketDoc.custom_end_time || "";
    fetchedLocationText.value = ticketDoc.custom_location_text || "";
    
    // GeoJSON (your existing code)
    if (ticketDoc.custom_location) {
      try {
        const geojson = JSON.parse(ticketDoc.custom_location);
        if (geojson.features?.[0]?.geometry?.coordinates) {
          const coords = geojson.features[0].geometry.coordinates;
          savedLongitude.value = coords[0];
          savedLatitude.value = coords[1];
        }
      } catch (e) {
        console.warn('GeoJSON parse failed:', e);
      }
    }
  } catch (e) {  // ✅ OUTER CATCH - UPDATE THIS ONE
    console.error("fetchTicketTimes failed:", e);
    // Fallback: safe "Start Ticket" state
    buttonState.value = { show: true, text: 'Start Ticket', isClose: false };
    showStartClose.value = true;
  }
};


onMounted(async () => {
  await fetchTicketTimes();
});


watch(
  () => props.ticketName,
  async (newName) => {
    if (newName) {
      await fetchTicketTimes();
    }
  }
);

watch(showLocationModal, async (isOpen) => {
  if (isOpen && savedLatitude.value && savedLongitude.value) {
    await nextTick();
    setTimeout(initializeMap, 200);
  } else if (!isOpen && mapInstance.value) {
    // Clean shutdown when closing
    try {
      mapInstance.value.stop();
      mapInstance.value.off();
      mapInstance.value.remove();
    } catch (e) {}
    mapInstance.value = null;
  }
});

watch(() => props.ticketStatus, async (newStatus, oldStatus) => {
  if (newStatus && newStatus !== oldStatus && props.ticketName) {
    console.log(`🔄 Auto-refresh: ${oldStatus || '?'} → ${newStatus}`);
    isStatusRefreshing.value = true;
    
    // 300ms delay + refresh
    await new Promise(resolve => setTimeout(resolve, 300));
    await fetchTicketTimes();
    
    // Brief success
    setTimeout(() => {
      isStatusRefreshing.value = false;
    }, 500);
  }
}, { immediate: true, flush: 'post' });

watch([() => props.ticketStatus, () => props.ticketName], async () => {
  if (props.ticketName) await fetchTicketTimes();
}, { immediate: true });



const handleButtonClick = async () => {
  if (isUpdating.value) return;
  if (buttonState.value.isClose) {
    showCloseModal.value = true;
  } else {
    await handleStartTicket();
  }
};



const defaultActions = computed(() => {
  let actions = [
    {
      icon: h(EmailIcon, { class: "h-4 w-4" }),
      label: "Email",
      onClick: () =>
        communicationAreaRef?.value?.toggleEmailBox() ?? toggleEmailBox(),
    },
    {
      icon: h(CommentIcon, { class: "h-4 w-4" }),
      label: "Comment",
      onClick: () =>
        communicationAreaRef?.value?.toggleCommentBox() ?? toggleCommentBox(),
    },
  ];
  if (isCallingEnabled.value) {
    actions.push(...callActions.value);
  }
  return actions;
});

const callActions = computed(() => [
  {
    icon: h(PhoneIcon, { class: "h-4 w-4" }),
    label: "Make a Call",
    onClick: () => makeCall && makeCall(),
  },
  {
    icon: "edit-3",
    label: "Log a Call",
    onClick: () => {
      showCallLogModal.value = true;
    },
  },
]);

const startTimeDisplay = computed(() => fetchedStartTime.value || props.customStartTime || '');
const endTimeDisplay = computed(() => fetchedEndTime.value || props.customEndTime || '');

const nowFrappeFormat = () => {
  const d = new Date();
  const pad = (n: number) => n.toString().padStart(2, "0");
  return (
    d.getFullYear() +
    "-" + pad(d.getMonth() + 1) +
    "-" + pad(d.getDate()) +
    " " + pad(d.getHours()) +
    ":" + pad(d.getMinutes()) +
    ":" + pad(d.getSeconds())
  );
};

const formatTime = (timeStr: string) => {
  if (!timeStr) return '';
  const date = new Date(timeStr);
  if (window.innerWidth < 768) {
    return date.toLocaleTimeString('en-IN', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  }
  return date.toLocaleString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  });
};



const captureCurrentLocation = () => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      console.warn("❌ Geolocation not supported");
      return resolve(null);
    }
    
    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        });
      },
      (error) => {
        console.warn("Location error:", error.code);
        resolve(null);  // Don't reject - continue without location
      },
      {
        enableHighAccuracy: false, 
        timeout: 10000,            
        maximumAge: 300000        
      }
    );
  });
};

const initializeMap = () => {
  if (!mapContainer.value || !savedLatitude.value || !savedLongitude.value) return;
  
  const lat = parseFloat(savedLatitude.value);
  const lng = parseFloat(savedLongitude.value);
  
  // Safe cleanup - stop all animations first
  if (mapInstance.value) {
    try {
      mapInstance.value.stop();
      mapInstance.value.off();
      mapInstance.value.remove();
    } catch (e) {}
    mapInstance.value = null;
  }
  
  // Create map
  mapInstance.value = L.map(mapContainer.value, {
    scrollWheelZoom: true,
    dragging: true,
    zoomControl: true,
    zoomAnimation: false  // Prevents animation errors
  }).setView([lat, lng], 15);
  
  // Tiles
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap',
    maxZoom: 19
  }).addTo(mapInstance.value);
  
  // Marker
  const markerIcon = L.divIcon({
    html: '<div style="width:40px;height:40px;background:linear-gradient(135deg,#ef4444,#dc2626);border-radius:50%;border:3px solid white;box-shadow:0 4px 12px rgba(239,68,68,0.5);display:flex;align-items:center;justify-content:center;font-size:18px;">📍</div>',
    className: '',
    iconSize: [40, 40],
    iconAnchor: [20, 40],
    popupAnchor: [0, -40]
  });
  
  L.marker([lat, lng], { icon: markerIcon }).addTo(mapInstance.value)
    .bindPopup(locationText.value || 'Agent Location')
    .openPopup();
  
  setTimeout(() => mapInstance.value?.invalidateSize(), 150);
};





const handleStartTicket = async () => {
  if (!props.ticketName || isUpdating.value) return;
  isUpdating.value = true;

  try {
    const currentTime = nowFrappeFormat();
    
    // ✅ ONE CALL does ToDo + status + time
    await call("test_app.api1.start_ticket", {
      ticket_name: props.ticketName
    });

    const location = await captureCurrentLocation();
    if (location?.latitude && location?.longitude) {
      console.log(`📍 Saving: ${location.latitude}, ${location.longitude}`);
      
      const result = await call("test_app.ticket_location.capture_agent_location", {
        ticket_name: props.ticketName,
        latitude: location.latitude,
        longitude: location.longitude,
      });
      
      // ✅ Show address immediately
      if (result?.message?.address) {
        fetchedLocationText.value = result.message.address;
        console.log("✅ Address:", result.message.address);
      }
    }

    isTicketStarted.value = true;
    await fetchTicketTimes();

    setTimeout(() => {
      window.location.reload();
    }, 100);
  } catch (e) {
    console.error("❌ Ticket start failed:", e);
    alert("Failed to start ticket");
  } finally {
    isUpdating.value = false;
  }
};




const onCloseWithComment = async (commentText: string) => {
  console.log('💬 Closing with comment:', commentText);
  
  if (!props.ticketName || isUpdating.value) return;
  
  isUpdating.value = true;
  try {
    const currentTime = nowFrappeFormat();
    
    await call("frappe.client.set_value", {
      doctype: "HD Ticket",
      name: props.ticketName,
      fieldname: "status",
      value: "Closed",
    });
    
    await call("frappe.client.set_value", {
      doctype: "HD Ticket",
      name: props.ticketName,
      fieldname: "custom_end_time",
      value: currentTime,
    });
    
    isTicketStarted.value = false;
    await fetchTicketTimes();
    
    console.log('✅ Ticket closed with comment');
    window.location.reload();
  } catch (e) {
    console.error("Close failed:", e);
    alert("Failed to close ticket");
  } finally {
    isUpdating.value = false;
  }
};
</script>
