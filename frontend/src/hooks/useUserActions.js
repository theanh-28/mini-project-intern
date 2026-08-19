import { useState } from 'react';
import { adminService } from '@/services/adminService';

export const useUserActions = ({ onRefresh, onUserUpdate, onDeleteSuccess } = {}) => {
    const [confirmModal, setConfirmModal] = useState(null); // { type: 'delete' | 'restore' | 'status' | 'reset-password', user: Object }
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [successMsg, setSuccessMsg] = useState(null);
    const [statusLoadingId, setStatusLoadingId] = useState(null);
    const [resetPasswordLoading, setResetPasswordLoading] = useState(false);
    const [actionFeedback, setActionFeedback] = useState({ msg: '', type: '' });

    const openDeleteModal = (user) => {
        setError(null);
        setSuccessMsg(null);
        setConfirmModal({ type: 'delete', user });
    };

    const openRestoreModal = (user) => {
        setError(null);
        setSuccessMsg(null);
        setConfirmModal({ type: 'restore', user });
    };

    const openStatusModal = (user) => {
        setError(null);
        setSuccessMsg(null);
        setConfirmModal({ type: 'status', user });
    };

    const openResetPasswordModal = (user) => {
        setError(null);
        setSuccessMsg(null);
        setConfirmModal({ type: 'reset-password', user });
    };

    const closeModal = () => {
        setConfirmModal(null);
        setError(null);
        setSuccessMsg(null);
    };

    // Bật / Tắt trạng thái is_active (Gọi PATCH /admin/users/:id/status)
    const handleToggleStatus = async (user) => {
        if (!user || statusLoadingId === user.user_id) return;

        setStatusLoadingId(user.user_id);
        setError(null);

        try {
            const nextStatus = !user.is_active;
            const updated = await adminService.updateUserStatus(user.user_id, nextStatus);
            user.is_active = nextStatus;

            if (onUserUpdate) {
                onUserUpdate((prev) => ({ ...prev, is_active: nextStatus }));
            }
            if (onRefresh) {
                onRefresh();
            }
            return updated;
        } catch (err) {
            const errData = err.response?.data?.error || err.response?.data?.detail || err.message;
            const errMsg = typeof errData === 'object'
                ? (Array.isArray(errData) ? errData[0]?.msg : errData.msg || errData.message || JSON.stringify(errData))
                : errData;
            setError(errMsg || 'Đổi trạng thái thất bại, vui lòng thử lại');
        } finally {
            setStatusLoadingId(null);
        }
    };

    // Admin gửi yêu cầu đặt lại mật khẩu (Gọi POST /admin/users/:id/reset-password)
    const handleResetPassword = async (userId) => {
        if (!userId || resetPasswordLoading) return;

        setResetPasswordLoading(true);
        setActionFeedback({ msg: '', type: '' });

        try {
            const res = await adminService.adminResetPassword(userId);
            setActionFeedback({ msg: res.message || 'Đã gửi hướng dẫn đặt lại mật khẩu!', type: 'success' });
            return res;
        } catch (err) {
            const errData = err.response?.data?.error || err.response?.data?.detail || err.message;
            const errMsg = typeof errData === 'object'
                ? (Array.isArray(errData) ? errData[0]?.msg : errData.msg || errData.message || JSON.stringify(errData))
                : errData;
            setActionFeedback({ msg: errMsg || 'Gửi yêu cầu reset mật khẩu thất bại', type: 'error' });
        } finally {
            setResetPasswordLoading(false);
        }
    };

    // Xác nhận hành động từ Confirm Modal (delete, restore, status, reset-password)
    const handleConfirm = async () => {
        if (!confirmModal?.user) return;

        const { type, user } = confirmModal;
        setLoading(true);
        setError(null);
        setSuccessMsg(null);

        try {
            if (type === 'delete') {
                await adminService.deleteUser(user.user_id);
                closeModal();
                if (onDeleteSuccess) {
                    onDeleteSuccess(user);
                } else if (onRefresh) {
                    onRefresh();
                }
                return;
            } else if (type === 'restore') {
                await adminService.restoreUser(user.user_id);
            } else if (type === 'status') {
                const nextStatus = !user.is_active;
                await adminService.updateUserStatus(user.user_id, nextStatus);
                user.is_active = nextStatus;
                if (onUserUpdate) {
                    onUserUpdate((prev) => ({ ...prev, is_active: nextStatus }));
                }
            } else if (type === 'reset-password') {
                const res = await adminService.adminResetPassword(user.user_id);
                setSuccessMsg(res.message || `Đã gửi hướng dẫn đặt lại mật khẩu đến email ${user.email}`);
                return;
            }

            closeModal();

            if (onRefresh) {
                onRefresh();
            }
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
        successMsg,
        statusLoadingId,
        resetPasswordLoading,
        actionFeedback,
        openDeleteModal,
        openRestoreModal,
        openStatusModal,
        openResetPasswordModal,
        closeModal,
        handleConfirm,
        handleToggleStatus,
        handleResetPassword,
    };
};
