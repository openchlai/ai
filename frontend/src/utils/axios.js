import axios from 'axios';

// Auto-detect baseURL
const isLocalhost = window.location.hostname === 'localhost' ||
  window.location.hostname === '127.0.0.1' ||
  window.location.hostname === '0.0.0.0';

const baseURL = import.meta.env.VITE_API_URL ||
  (isLocalhost ?  'http://Localhost:8520/api/v1' : window.location.origin);

const axiosInstance = axios.create({
  baseURL,
  timeout: 10000, // 10 seconds timeout
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Request interceptor
axiosInstance.interceptors.request.use(
  (config) => {
    // Log request details in development
    if (import.meta.env.DEV) {
      console.log('Request:', {
        url: config.url,
        method: config.method,
        data: config.data,
        params: config.params
      });
    }

    // Add authorization token if available
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    return config;
  },
  (error) => {
    if (import.meta.env.DEV) {
      console.error('Request Error Interceptor:', error);
    }
    return Promise.reject(error);
  }
);

// Response interceptor
axiosInstance.interceptors.response.use(
  (response) => {
    // Log response details in development
    if (import.meta.env.DEV) {
      console.log('Response:', {
        status: response.status,
        data: response.data,
        url: response.config.url
      });
    }
    return response;
  },
  async (error) => {
    if (import.meta.env.DEV) {
      console.error('Response Error Interceptor:', error);
    }

    const originalRequest = error.config;
    const status = error.response?.status;

    // Handle token refresh when access token expires
    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) throw new Error('No refresh token available');

        // Request new access token
        const response = await axios.post(`${baseURL}/auth/token/refresh/`, {
          refresh: refreshToken
        });

        // Store new tokens
        localStorage.setItem('access_token', response.data.access);
        if (response.data.refresh) {
          localStorage.setItem('refresh_token', response.data.refresh);
        }

        // Update authorization header
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;

        // Retry original request
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        // Token refresh failed - clear storage and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');

        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
        }
        return Promise.reject(refreshError);
      }
    }

    // Handle other error cases
    if (status === 403) {
      return Promise.reject(new Error('You do not have permission to access this resource.'));
    }

    if (status === 404) {
      return Promise.reject(new Error('The requested resource was not found.'));
    }

    if (status === 429) {
      const retryAfter = error.response.headers['retry-after'] || 5;
      return Promise.reject(new Error(`Too many requests. Please try again after ${retryAfter} seconds.`));
    }

    if (status >= 500) {
      return Promise.reject(new Error('A server error occurred. Please try again later.'));
    }

    if (error.code === 'ECONNABORTED') {
      return Promise.reject(new Error('Request timeout. Please check your network connection.'));
    }

    if (!error.response) {
      return Promise.reject(new Error('Network error. Please check your internet connection.'));
    }

    return Promise.reject(error);
  }
);

export default axiosInstance;