import axios from 'axios';

const axiosInstance = axios.create({
    // Always use relative path - nginx will proxy it
    baseURL: '/api-proxy',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
});

// Add session-id to all requests if available
axiosInstance.interceptors.request.use((config) => {
    // Add Session-Id header if available
    const sessionId = localStorage.getItem('session-id');
    if (sessionId) {
        config.headers['Session-Id'] = sessionId;
    }
    // Add X-API-Key for /cases/ endpoint
    if (config.url.includes('/cases/')) {
        config.headers['X-API-Key'] = '08m9cujgjlk0epqqms1q99bbvc';
    }
    
    return config;
}, (error) => Promise.reject(error));

// Add response interceptor for better error handling
axiosInstance.interceptors.response.use(
    (response) => response,
    (error) => {
        // Handle 401 Unauthorized - redirect to login
        if (error.response?.status === 401) {
            localStorage.removeItem('session-id');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Dashboard data fetchers
export async function fetchCasesData() {
    try {
        const { data } = await axiosInstance.get("/api/wallonly/rpt", {
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
        const { data } = await axiosInstance.get("/api/wallonly/rpt", {
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