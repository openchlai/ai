import axios from 'axios';

const username = 'test';
const password = 'p@ssw0rd';

const axiosInstance = axios.create({
    baseURL: process.env.NODE_ENV === 'development'
        ? '/api-proxy'
        : 'https://demo-openchs.bitz-itc.com/helpline/',
    timeout: 10000,
    auth: {
        username,
        password
    },
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
});

axiosInstance.interceptors.request.use((config) => {
    // Add X-API-Key for /cases/ endpoint
    if (config.url.includes('/cases/')) {
        config.headers['X-API-Key'] = '08m9cujgjlk0epqqms1q99bbvc';
    }
    return config;
}, (error) => Promise.reject(error));

export default axiosInstance;

// import axios from 'axios'

// const axiosInstance = axios.create({
//   baseURL: 'https://demo-openchs.bitz-itc.com/helpline/', // ✅ use your real base URL
//   headers: {
//     'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe', // ✅ always sent
//     'Content-Type': 'application/json',
//   },
// })

// Optional: log requests & responses for debugging
// axiosInstance.interceptors.request.use((config) => {
//   console.log('📤 Request:', config)
//   return config
// })

// axiosInstance.interceptors.response.use(
//   (response) => {
//     console.log('📥 Response:', response)
//     return response
//   },
//   (error) => {
//     console.error('❌ API Error:', error.response || error.message)
//     return Promise.reject(error)
//   }
// )

// export default axiosInstance

