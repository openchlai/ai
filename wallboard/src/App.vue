<template>
  <div class="container" :class="{ 'dark-mode': isDarkMode }">
    <Header :isDarkMode="isDarkMode" :connectionClass="connectionClass" :connectionLabel="connectionLabel"
      :lastUpdate="lastUpdate" @toggleDarkMode="toggleDarkMode" />

    <CasesGrid :casesTiles="casesTiles" />
    <TopStats :stats="stats" />
    <CounsellorsTable :counsellors="counsellorsWithQueueData" :count="onlineCounsellorsCount"
      :statusClass="statusClass" />
    <CallersTable :callers="callersData" :count="onlineCallersCount" :statusClass="statusClass" />
  </div>
</template>

<script setup>
  import { ref, computed, onMounted } from "vue";
  import { useQueueMonitor } from "@/composables/useQueueMonitor.js";
  import { fetchCasesData } from "@/utils/axios.js";
  import CallersTable from "@/components/CallersTable.vue";
  import CounsellorsTable from "@/components/CounsellorsTable.vue";
  import CasesGrid from "@/components/CasesGrid.vue";
  import TopStats from "@/components/TopStats.vue";
  import Header from "@/components/Header.vue";

  const isDarkMode = ref(false);

  // --- WebSocket state ---
  const { wsReady, channels, lastUpdate } = useQueueMonitor();

  // --- REST API state ---
  const apiData = ref(null);
  const apiError = ref(null);

  async function loadCases() {
    try {
      apiData.value = await fetchCasesData();
    } catch (err) {
      apiError.value = err.message;
    }
  }

  // --- Derived from API ---
  const casesTiles = computed(() => {
    const stats = apiData.value?.stats || {};
    return [
      { id: "ct1", label: "TODAY'S ANSWERED CALLS", value: stats.calls_today || "--", variant: "c-blue" },
      { id: "ct2", label: "TODAY'S CASES", value: stats.cases_today || "--", variant: "c-amber" },
      { id: "ct3", label: "ONGOING CASES", value: stats.cases_ongoing_total || "--", variant: "c-red" },
      { id: "ct4", label: "MONTH CLOSED CASES", value: stats.cases_closed_this_month || "--", variant: "c-green" },
      { id: "ct5", label: "TOTAL CALLS", value: stats.calls_total || "--", variant: "c-black" },
      { id: "ct6", label: "TOTAL CASES", value: stats.cases_total || "--", variant: "c-black" },
    ];
  });

  // --- Derived from WebSocket ---
  const counsellorsWithQueueData = computed(() =>
    (channels.value || []).filter(
      (c) => (c.CHAN_CONTEXT || "").toLowerCase() === "agentlogin"
    )
  );

  const callersData = computed(() =>
    (channels.value || []).filter(
      (c) => (c.CHAN_CONTEXT || "").toLowerCase() === "dlpn_callcenter"
    )
  );

  // --- Stats row from channel data ---
  const stats = computed(() => [
    { id: 1, title: "Total", value: (channels.value || []).length.toString(), variant: "total" },
    { id: 2, title: "Connected", value: (channels.value || []).filter((c) => c.CHAN_STATE_CONNECT).length.toString(), variant: "answered" },
    { id: 3, title: "In Queue", value: (channels.value || []).filter((c) => c.CHAN_STATE_QUEUE).length.toString(), variant: "abandoned" },
  ]);

  // --- Counts ---
  const onlineCounsellorsCount = computed(() => counsellorsWithQueueData.value.length);
  const onlineCallersCount = computed(() => callersData.value.length);

  // --- Helpers ---
  function statusClass(status) {
    const s = (status || "").toLowerCase();
    if (s.includes("on call")) return "status-oncall";
    if (s.includes("ring")) return "status-ringing";
    if (s.includes("queue")) return "status-inqueue";
    if (s.includes("available")) return "status-available";
    if (s.includes("offline")) return "status-offline";
    return "status-neutral";
  }

  function applyThemeClass() {
    document.documentElement.classList.toggle("dark-mode", isDarkMode.value);
  }

  function toggleDarkMode() {
    isDarkMode.value = !isDarkMode.value;
    localStorage.setItem("darkMode", isDarkMode.value.toString());
    applyThemeClass();
  }

  // --- Lifecycle ---
  onMounted(() => {
    // restore theme
    const saved = localStorage.getItem("darkMode");
    if (saved !== null) isDarkMode.value = saved === "true";
    applyThemeClass();

    // fetch cases once + every 5 minutes
    loadCases();
    setInterval(loadCases, 300000);
  });

  // --- Connection label ---
  const connectionClass = computed(() =>
    wsReady.value === "open" ? "on" : wsReady.value === "connecting" ? "connecting" : "off"
  );

  const connectionLabel = computed(() => {
    if (wsReady.value === "connecting") return "Connecting...";
    if (wsReady.value === "open") return "Connected";
    if (wsReady.value === "error") return "Error";
    return "Disconnected";
  });
</script>
