import axios from "axios";

const username = "test";
const password = "p@ssw0rd";

const axiosInstance = axios.create({
    baseURL:
        import.meta.env.MODE === "development"
            ? "/api-proxy"
            // : "https://demo-openchs.bitz-itc.com/helpline/",
            : "https://helpline.sematanzania.org/helpline/",
    timeout: 10000,
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

// For dashboard tiles (example: today’s summary)
export async function fetchCasesData() {
    try {
        const { data } = await axiosInstance.get("/api/wallonly/rpt", {
            params: {
                dash_period: "today",
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
        console.error("Error fetching wallboard report:", err.message);
        return null;
    }
}

export default axiosInstance;
