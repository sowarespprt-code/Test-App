<template>
  <div
    class="md:mx-10 md:my-4 flex items-center justify-between text-lg font-medium mx-6 mb-4 !mt-8"
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
          'focus:outline-none focus:ring-2 focus:ring-offset-1',
          'touch-manipulation',
          isUpdating 
            ? 'bg-gray-400 text-white cursor-not-allowed' 
            : isTicketStarted 
              ? 'bg-red-500 hover:bg-red-600 text-white focus:ring-red-500' 
              : 'bg-green-500 hover:bg-green-600 text-white focus:ring-green-500'
        ]"
        style="pointer-events: auto; -webkit-tap-highlight-color: transparent; user-select: none;"
        @click.stop="handleButtonClick"
      >
        {{ isUpdating 
          ? (isTicketStarted ? 'Closing...' : 'Starting...') 
          : (isTicketStarted ? 'Close Ticket' : 'Start Ticket') }}
      </button>

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
const startedStatuses = ["In Progress", "Replied", "Resolved"];
const isUpdating = ref(false);

const fetchedStartTime = ref("");
const fetchedEndTime = ref("");
const fetchedLocationText = ref("");

const showLocationModal = ref(false);
const mapContainer = ref(null);
const mapInstance = ref(null);
const savedLatitude = ref(null);
const savedLongitude = ref(null);


const locationText = computed(() => {
  return fetchedLocationText.value || '';
});

// Update fetchTicketTimes:
const fetchTicketTimes = async () => {
  if (!props.ticketName) return;
  
  try {
    const result = await call("frappe.client.get_value", {
      doctype: "HD Ticket",
      filters: { name: props.ticketName },
      fieldname: ["custom_start_time", "custom_end_time", "custom_location_text", "custom_location"]
    });
    
    if (result) {
      fetchedStartTime.value = result.custom_start_time || "";
      fetchedEndTime.value = result.custom_end_time || "";
      fetchedLocationText.value = result.custom_location_text || "";
      
      // Parse GeoJSON to extract lat/lng
      if (result.custom_location) {
        try {
          const geojson = JSON.parse(result.custom_location);
          if (geojson.features && geojson.features[0]?.geometry?.coordinates) {
            const coords = geojson.features[0].geometry.coordinates;
            savedLongitude.value = coords[0];  // GeoJSON: [lng, lat]
            savedLatitude.value = coords[1];
            console.log('📍 Parsed from GeoJSON:', savedLatitude.value, savedLongitude.value);
          }
        } catch (e) {
          console.warn('GeoJSON parse failed:', e);
        }
      }
    }
  } catch (e) {
    console.error("Failed to fetch ticket data:", e);
  }
};



onMounted(async () => {
  syncButtonWithStatus();
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

watch(
  () => props.ticketStatus,
  () => {
    syncButtonWithStatus();
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


const handleButtonClick = async () => {
  if (isUpdating.value) return;
  
  if (isTicketStarted.value) {
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

const syncButtonWithStatus = () => {
  const status = props.ticketStatus;
  isTicketStarted.value = startedStatuses.includes(status);
};

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

const showStartClose = computed(() => {
  const status = props.ticketStatus;
  const hiddenStatuses = ["Closed", "Resolved", ""];
  return !hiddenStatuses.includes(status);
});

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

    await call("frappe.client.set_value", {
      doctype: "HD Ticket",
      name: props.ticketName,
      fieldname: "status",
      value: "In Progress",
    });

    await call("frappe.client.set_value", {
      doctype: "HD Ticket",
      name: props.ticketName,
      fieldname: "custom_start_time",
      value: currentTime,
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
    }, 2000);
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
