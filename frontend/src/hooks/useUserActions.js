import { useState } from 'react';
import { adminService } from '@/services/adminService';

export const useUserActions = () => {
    const [confirmModal, setConfirmModal] = useState(null); // { type: 'delete' | 'restore', user: Object }
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const openDeleteModal = (user) => {
        setError(null);
        setConfirmModal({ type: 'delete', user });
    };

    const openRestoreModal = (user) => {
        setError(null);
        setConfirmModal({ type: 'restore', user });
    };

    const closeModal = () => {
        setConfirmModal(null);
        setError(null);
    };

    const handleConfirm = async () => {
        if (!confirmModal?.user) return;

        const { type, user } = confirmModal;
        setLoading(true);
        setError(null);

        try {
            if (type === 'delete') {
                await adminService.deleteUser(user.user_id);
                user.is_active = false;
            } else if (type === 'restore') {
                await adminService.restoreUser(user.user_id);
                user.is_active = true;
            }

            closeModal();
        } catch (err) {
            const errData = err.response?.data?.error || err.response?.data?.detail || err.message;
            const errMsg = typeof errData === 'object' 
                ? (Array.isArray(errData) ? errData[0]?.msg : errData.msg || errData.message || JSON.stringify(errData)) 
                : errData;
            setError(errMsg || 'Thao tác thất bại, vui lòng thử lại');
        } finally {
            setLoading(false);
        }
    };

    return {
        confirmModal,
        loading,
        error,
        openDeleteModal,
        openRestoreModal,
        closeModal,
        handleConfirm,
    };
};
