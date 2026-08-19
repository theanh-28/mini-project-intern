import api from './api';

export const authService = {
    login: async (email, password) => {
        const response = await api.post('/auth/login', {email, password});
        return response.data;
    },
    logout: async () => {
        return await api.post('/auth/logout');
    },
    forgotPassword: async (email) => {
        const response = await api.post('/auth/forgot-password', { email });
        return response.data;
    },
    resetPassword: async (token, newPassword, confirmPassword) => {
        const response = await api.post('/auth/reset-password', {
            reset_token:token,
            new_password: newPassword,
            confirm_password: confirmPassword,
        });
        return response.data;
    },
};