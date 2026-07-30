import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    headers: {
        'Content-type': 'application/json',
    },
});

// Resquest Interceptor: Tự động đính thêm token JWT vào mỗi request
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => Promise.reject(error)
)

// Response Interceptor: Xử lý các lỗi trả về toàn cục
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            const url = error.config?.url || '';

            // Request đăng nhập bị 401 (sai mật khẩu)
            if (url.includes('/auth/')) {
                return Promise.reject(error);
            }

            // Các API khác bị 401 (token hết hạn hoặc bị thu hồi)
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/auth/login';
        }

        return Promise.reject(error);
    }
);

export default api;