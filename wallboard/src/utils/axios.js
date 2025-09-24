import axios from "axios";

/**
 * This file creates and configures an Axios instance for making API requests.
 */

const username = "test";
const password = "p@ssw0rd";

/**
 * A pre-configured Axios instance with a base URL, timeout, and authentication headers.
 */
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

/**
 * A request interceptor that adds an `X-API-Key` header to requests that include `/cases/` in their URL.
 */
axiosInstance.interceptors.request.use(
    (config) => {
        if (config.url && config.url.includes("/cases/")) {
            config.headers["X-API-Key"] = "08m9cujgjlk0epqqms1q99bbvc";
        }
        return config;
    },
    (error) => Promise.reject(error)
);

/**
 * Fetches the wallboard report data.
 * @returns {Promise<object|null>} The data from the API, or null if an error occurs.
 */
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
