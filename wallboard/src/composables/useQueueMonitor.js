import { ref, onMounted, onBeforeUnmount } from "vue";

export function useQueueMonitor() {
    const wsReady = ref("closed");
    const channels = ref([]);
    const lastUpdate = ref(null);

    const WSHOST = "wss://helpline.sematanzania.org:8384/ami/sync?c=-2&";
    let ws = null;
    let reconnectTimer = null;

    function connect() {
        if (ws && wsReady.value === "open") return;
        wsReady.value = "connecting";
        ws = new WebSocket(WSHOST);

        ws.onopen = () => {
            wsReady.value = "open";
        };

        ws.onmessage = (ev) => {
            try {
                const payload = JSON.parse(ev.data);
                channels.value = Array.isArray(payload.channels) ? payload.channels : [];
                lastUpdate.value = new Date().toLocaleString();
            } catch (err) {
                console.error("WS parse error:", err);
            }
        };

        ws.onclose = () => {
            wsReady.value = "closed";
            scheduleReconnect();
        };

        ws.onerror = () => {
            wsReady.value = "error";
        };
    }

    function scheduleReconnect() {
        if (reconnectTimer) return;
        reconnectTimer = setTimeout(() => {
            reconnectTimer = null;
            connect();
        }, 5000);
    }

    function disconnect() {
        if (ws) {
            ws.close();
            ws = null;
        }
        if (reconnectTimer) {
            clearTimeout(reconnectTimer);
            reconnectTimer = null;
        }
        wsReady.value = "closed";
    }

    onMounted(connect);
    onBeforeUnmount(disconnect);

    return {
        wsReady,
        channels,
        lastUpdate,
    };
}
