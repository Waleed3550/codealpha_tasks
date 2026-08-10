import axios from 'axios';
import { useAuthStore } from '@/store/useAuthStore';

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request Interceptor: Attach JWT Token
api.interceptors.request.use(
    (config) => {
        const token = useAuthStore.getState().accessToken;
        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401s and Automatic Token Refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        
        const isAuthEndpoint = originalRequest?.url?.includes('/auth/login') ||
                               originalRequest?.url?.includes('/auth/refresh') ||
                               originalRequest?.url?.includes('/auth/register');

        if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
            originalRequest._retry = true;
            
            try {
                // The refresh token is sent automatically via HttpOnly cookie
                const response = await axios.post(`${api.defaults.baseURL}/auth/refresh/`, {}, {
                    withCredentials: true
                });
                
                const { access } = response.data;
                // Update Zustand store with new access token
                useAuthStore.getState().setAccessToken(access);
                
                // Retry original request
                originalRequest.headers.Authorization = `Bearer ${access}`;
                return api(originalRequest);
                
            } catch (refreshError) {
                // Refresh token expired or invalid - force logout
                useAuthStore.getState().logout();
                if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
                    window.location.href = '/login';
                }
                return Promise.reject(refreshError);
            }
        }
        
        return Promise.reject(error);
    }
);

export default api;
