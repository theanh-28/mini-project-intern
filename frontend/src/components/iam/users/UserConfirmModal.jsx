import Button from '@/components/common/Button';
import { CircleCheck } from 'lucide-react';
import styles from './UserConfirmModal.module.css';

export default function UserConfirmModal({
    confirmState,
    loading,
    error,
    successMsg,
    onConfirm,
    onClose,
}) {
    if (!confirmState) return null;

    const { type, user } = confirmState;

    let title = 'Confirm Action';
    let message = 'Are you sure you want to perform this action?';
    let confirmText = 'Confirm';
    let confirmBtnClass = styles.restoreBtn;

    if (type === 'delete') {
        title = 'Confirm Delete User';
        message = 'Are you sure you want to delete this user?';
        confirmText = 'Delete';
        confirmBtnClass = styles.deleteBtn;
    } else if (type === 'restore') {
        title = 'Confirm Restore User';
        message = 'Are you sure you want to restore this user?';
        confirmText = 'Restore';
        confirmBtnClass = styles.restoreBtn;
    } else if (type === 'status') {
        if (user?.is_active) {
            title = 'Confirm Deactivate User';
            message = 'Are you sure you want to deactivate this user account?';
            confirmText = 'Deactivate';
            confirmBtnClass = styles.deleteBtn;
        } else {
            title = 'Confirm Activate User';
            message = 'Are you sure you want to activate this user account?';
            confirmText = 'Activate';
            confirmBtnClass = styles.restoreBtn;
        }
    } else if (type === 'reset-password') {
        title = 'Confirm Reset Password';
        message = 'Are you sure you want to send password reset instructions to this user?';
        confirmText = 'Send Reset Link';
        confirmBtnClass = styles.restoreBtn;
    }

    return (
        <div className={styles.modalOverlay}>
            <section className={styles.card}>
                <header className={styles.title}>
                    {title}
                </header>

                <div className={styles.body}>
                    {successMsg ? (
                        <div className={styles.successContainer}>
                            <CircleCheck size={40} color="var(--color-success, #16a34a)" className={styles.successIcon} />
                            <div className={styles.successTitle}>Yêu cầu đã được gửi!</div>
                            <div className={styles.successMsgText}>{successMsg}</div>
                        </div>
                    ) : (
                        <>
                            <p>{message}</p>
                            {user && (
                                <div className={styles.userInfo}>
                                    <div><strong>Name:</strong> {user.name}</div>
                                    <div><strong>Email:</strong> {user.email}</div>
                                </div>
                            )}

                            {error && <div className={styles.errorMsg}>{error}</div>}
                        </>
                    )}
                </div>

                <div className={styles.btns}>
                    {successMsg ? (
                        <Button 
                            className={`${styles.btn} ${styles.closeSuccessBtn}`} 
                            type="button" 
                            onClick={onClose}
                        >
                            Đóng
                        </Button>
                    ) : (
                        <>
                            <Button 
                                className={`${styles.btn} ${styles.cancelBtn}`} 
                                type="button" 
                                onClick={onClose} 
                                disabled={loading}
                            >
                                Cancel
                            </Button>
                            <Button 
                                className={`${styles.btn} ${confirmBtnClass}`} 
                                type="button" 
                                onClick={onConfirm} 
                                isLoading={loading}
                            >
                                {confirmText}
                            </Button>
                        </>
                    )}
                </div>
            </section>
        </div>
    );
}
