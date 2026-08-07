import Button from '@/components/common/Button';
import styles from './UserConfirmModal.module.css';

export default function UserConfirmModal({
    confirmState,
    loading,
    error,
    onConfirm,
    onClose,
}) {
    if (!confirmState) return null;

    const { type, user } = confirmState;
    const isDelete = type === 'delete';

    return (
        <div className={styles.modalOverlay}>
            <section className={styles.card}>
                <header className={styles.title}>
                    {isDelete ? 'Confirm Delete User' : 'Confirm Restore User'}
                </header>

                <div className={styles.body}>
                    <p>
                        Are you sure you want to {isDelete ? 'delete' : 'restore'} this user?
                    </p>
                    {user && (
                        <div className={styles.userInfo}>
                            <div><strong>Name:</strong> {user.name}</div>
                            <div><strong>Email:</strong> {user.email}</div>
                        </div>
                    )}

                    {error && <div className={styles.errorMsg}>{error}</div>}
                </div>

                <div className={styles.btns}>
                    <Button 
                        className={`${styles.btn} ${styles.cancelBtn}`} 
                        type="button" 
                        onClick={onClose} 
                        disabled={loading}
                    >
                        Cancel
                    </Button>
                    <Button 
                        className={`${styles.btn} ${isDelete ? styles.deleteBtn : styles.restoreBtn}`} 
                        type="button" 
                        onClick={onConfirm} 
                        isLoading={loading}
                    >
                        {isDelete ? 'Delete' : 'Restore'}
                    </Button>
                </div>
            </section>
        </div>
    );
}
