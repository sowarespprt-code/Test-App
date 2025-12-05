<template>
  <FrappeUIProvider>


    <PortalRoot />
  </FrappeUIProvider>
  <KeymapDialog />
  <Dialogs />
</template>

<script setup lang="ts">
import { Dialogs } from "@/components/dialogs";
import KeymapDialog from "@/pages/KeymapDialog.vue";
import { useConfigStore } from "@/stores/config";
import { stopSession } from "@/telemetry";
import { FrappeUIProvider, toast } from "frappe-ui";
import { computed, defineAsyncComponent, h, ref, onMounted, onUnmounted } from "vue";
import Wifi from "~icons/lucide/wifi";
import WifiOff from "~icons/lucide/wifi-off";
import { useAuthStore } from "./stores/auth";
useConfigStore();

const isDark = ref(false);

const toggleTheme = () => {
  isDark.value = !isDark.value;

  if (isDark.value) {
    document.documentElement.classList.add("dark");
    localStorage.setItem("helpdesk_theme", "dark");
  } else {
    document.documentElement.classList.remove("dark");
    localStorage.setItem("helpdesk_theme", "light");
  }
};

onMounted(() => {
  window.addEventListener("online", () => {
    toast.create({
      message: "You are now online",
      icon: h(Wifi),
    });
  });

  window.addEventListener("offline", () => {
    toast.create({
      message: "You are now offline",
      icon: h(WifiOff),
    });
  });
  const savedTheme = localStorage.getItem("helpdesk_theme");
  if (savedTheme === "dark") {
    isDark.value = true;
    document.documentElement.classList.add("dark");
  }
});


const AgentPortalRoot = defineAsyncComponent(
  () => import("@/pages/desk/AgentRoot.vue")
);
const CustomerPortalRoot = defineAsyncComponent(
  () => import("@/pages/CustomerPortalRoot.vue")
);

const PortalRoot = computed(() => {
  const authStore = useAuthStore();
  if (authStore.hasDeskAccess && authStore.isAgent) {
    return AgentPortalRoot;
  } else {
    return CustomerPortalRoot;
  }
});

onUnmounted(() => {
  stopSession();
});
</script>
