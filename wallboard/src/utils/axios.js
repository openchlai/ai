import axios from "axios";

const username = "test";
const password = "p@ssw0rd";

const axiosInstance = axios.create({
    baseURL: __APP_API_BASE_URL__,
    timeout: 30000,
    auth: { username, password },
    headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
    },
});

axiosInstance.interceptors.request.use(
    (config) => {
        if (config.url && config.url.includes("/cases/")) {
            config.headers["X-API-Key"] = "08m9cujgjlk0epqqms1q99bbvc";
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// This fetches the main dashboard/cases statistics
export async function fetchCasesData() {
    try {
        const { data } = await axiosInstance.get("/rpt", {
            params: {

                dash_period: "today",  // ← Add this back
                type: "bar",
                stacked: "stacked",
                xaxis: "hangup_status_txt",
                yaxis: "h",
                vector: 1,
                rpt: "call_count",
                metrics: "call_count",
            },
        });
        return data;
    } catch (err) {
        console.error("Error fetching cases data:", err.message);
        console.error("Full error:", err);
        return null;
    }
}

// This fetches the calls report data for the status cards
export async function fetchCallsReportData() {
    try {
        const params = {
            dash_period: "today",
            type: "bar",
            stacked: "stacked",
            xaxis: "hangup_status_txt",
            yaxis: "h",
            vector: 1,
            rpt: "call_count",
            metrics: "call_count",
        }
        console.log('AXIOS FETCH REPORT DATA REQUEST:', params)
        const { data } = await axiosInstance.get("/rpt", { params });

        console.log('AXIOS FETCH REPORT DATA SUCCESS:', data)
        return data;

    } catch (err) {
        console.error("Error fetching calls report data:", err.message);
        console.error("Full error:", err);
        return null;
    }
}

export default axiosInstance;