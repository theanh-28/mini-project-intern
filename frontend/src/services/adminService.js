import api from './api';

export const adminService = {
    getUsers: async ({page = 1, per_page = 20}) => {
        const response = await api.get(`/admin/users?page=${page}&per_page=${per_page}`);
        return response.data;
    },
    createUser: async (userData) => {
        const response = await api.post('/admin/users', userData);
        return response.data;
    },
    deleteUser: async (userId) => {
        const response = await api.delete(`/admin/users/${userId}`);
    } ,
    restoreUser: async (userId) => {
        const response = await api.post(`/admin/users/${userId}/restore`);
    },
    getUserById: async (userId) => {
        const response = await api.get(`/admin/users/${userId}`);
        return response.data;
    },
    updateUser: async ({userData, userId}) => {
        const response = await api.put(`/admin/users/${userId}`, userData);
        return response.data;
    },
}   