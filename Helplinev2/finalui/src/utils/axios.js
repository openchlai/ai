import axios from 'axios';

const axiosInstance = axios.create({
    // Always use relative path - nginx will proxy it
    baseURL: '/api-proxy',
    timeout: 60000,
    withCredentials: true, // Required for legacy session cookie support
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
});

// Request interceptor
axiosInstance.interceptors.request.use((config) => {
    return config;
}, (error) => Promise.reject(error));

// Response interceptor for session/error management
axiosInstance.interceptors.response.use(
    (response) => response,
    (error) => {
        const status = error.response?.status;

        // 401 Unauthorized - redirect to login
        if (status === 401) {
            console.warn('⚠️ Session expired or unauthorized. Redirecting to login.');
            // Only redirect if not already on login page to avoid loops
            if (!window.location.pathname.startsWith('/login')) {
                window.location.href = '/login';
            }
        }

        // 412 Precondition Failed - Often used by legacy system for validation/logic errors
        if (status === 412) {
            const message = error.response?.data?.message || 'A validation error occurred.';
            console.error('❌ Legacy Validation Error (412):', message);
        }

        return Promise.reject(error);
    }
);

// Dashboard data fetchers
export async function fetchCasesData() {
    try {
        const { data } = await axiosInstance.get("api/wallonly/rpt", {
            params: {
                dash_period: "today",
                type: "bar",
                stacked: "stacked",
                xaxis: "hangup_status_txt",
                yaxis: "-",
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

export async function fetchCallsReportData() {
    try {
        const { data } = await axiosInstance.get("api/wallonly/rpt", {
            params: {
                dash_period: "today",
                type: "bar",
                stacked: "stacked",
                xaxis: "hangup_status_txt",
                yaxis: "-",
                vector: 1,
                rpt: "call_count",
                metrics: "call_count",
            },
        });

        return data;

    } catch (err) {
        console.error("Error fetching calls report data:", err.message);
        console.error("Full error:", err);
        return null;
    }
}

export default axiosInstance;