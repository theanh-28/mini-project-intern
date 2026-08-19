import api from './api';

export const adminService = {
    getUsers: async ({ page = 1, per_page = 20, search = '', status = '', role = '', startDate = '', endDate = '' }) => {
        const is_active = status === 'active' ? true : status === 'inactive' ? false : undefined;

        const response = await api.get('/admin/users', {
            params: {
                page,
                per_page,
                search:          search    || undefined,
                is_active:       is_active,
                role:            role      || undefined,
                created_at_from: startDate || undefined,
                created_at_to:   endDate   || undefined,
            },
        });
        return response.data;
    },
    createUser: async (userData) => {
        const response = await api.post('/admin/users', userData);
        return response.data;
    },
    deleteUser: async (userId) => {
        const response = await api.delete(`/admin/users/${userId}`);
        return response.data;
    },
    restoreUser: async (userId) => {
        const response = await api.post(`/admin/users/${userId}/restore`);
        return response.data;
    },
    getUserById: async (userId) => {
        const response = await api.get(`/admin/users/${userId}`);
        return response.data;
    },
    updateUser: async ({ userData, userId }) => {
        const response = await api.put(`/admin/users/${userId}`, userData);
        return response.data;
    },
    updateUserStatus: async (userId, isActive) => {
        const response = await api.patch(`/admin/users/${userId}/status`, { is_active: isActive });
        return response.data;
    },
    adminResetPassword: async (userId) => {
        const response = await api.post(`/admin/users/${userId}/reset-password`);
        return response.data;
    },
};