import { ref, onMounted, onBeforeUnmount } from "vue";

/**
 * A composable that manages the WebSocket connection and provides real-time queue data.
 */
export function useQueueMonitor() {
    /**
     * The connection status of the WebSocket.
     * @type {import('vue').Ref<string>}
     */
    const wsReady = ref("closed");
    /**
     * An array of channel data from the WebSocket.
     * @type {import('vue').Ref<Array>}
     */
    const channels = ref([]);
    /**
     * The timestamp of the last update from the WebSocket.
     * @type {import('vue').Ref<string|null>}
     */
    const lastUpdate = ref(null);

    const WSHOST = "wss://helpline.sematanzania.org:8384/ami/sync?c=-2&";
    let ws = null;
    let reconnectTimer = null;

    /**
     * Establishes the WebSocket connection.
     */
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

    /**
     * Schedules a reconnection attempt after a delay.
     */
    function scheduleReconnect() {
        if (reconnectTimer) return;
        reconnectTimer = setTimeout(() => {
            reconnectTimer = null;
            connect();
        }, 5000);
    }

    /**
     * Closes the WebSocket connection and clears any reconnection timers.
     */
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

    // Connect on mount, disconnect on unmount.
    onMounted(connect);
    onBeforeUnmount(disconnect);

    /**
     * Returns the WebSocket status, channel data, and last update timestamp.
     */
    return {
        wsReady,
        channels,
        lastUpdate,
    };
}
