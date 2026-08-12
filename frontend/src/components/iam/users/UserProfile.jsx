import { 
    User, 
    Shield, 
    CircleCheck, 
    Ban, 
    Pencil,
    KeyRound,
    RotateCcw,
} from 'lucide-react';

import styles from './UserProfile.module.css';
import Avatar from '@/components/common/Avatar';
import Button from '@/components/common/Button';
import UserUpdateModal from '@/components/iam/users/UserUpdateModal';
import UserConfirmModal from '@/components/iam/users/UserConfirmModal';

import { useUpdateUser } from '@/hooks/useUpdateUser';
import { useUserActions } from '@/hooks/useUserActions';

export default function UserProfile({
    user = {},
    setUser,
}) {

    const updateUser = useUpdateUser({user: user, setUser: setUser});

    const {
        confirmModal,
        loading: actionLoading,
        error: actionError,
        openDeleteModal,
        openRestoreModal,
        closeModal,
        handleConfirm,
    } = useUserActions();

    if (!user || Object.keys(user).length === 0) return null;

    return (
        <>
            <div className={styles.card}>
                <div className={styles.avatar}>
                    <Avatar name={user.name} size='lg' />
                    <span className={styles.userName}>
                        {user.name}
                    </span>
                    <span className={styles.userId}>
                        {user.user_id}
                    </span>
                </div>

                <div className={styles.userInfo}>
                    <div className={styles.infoRow}>
                        <span className={styles.label}>Email</span>
                        <span className={styles.value}>{user.email}</span>
                    </div>

                    <div className={styles.infoRow}>
                        <span className={styles.label}>Status</span>
                        <span className={styles.status}>
                            {user.is_active ? (
                                <div className={styles.statusActive}>
                                    <CircleCheck strokeWidth={3} size={15} color='var(--color-success)' /> Active
                                </div>
                            ) : (
                                <div className={styles.statusInactive}>
                                    <Ban strokeWidth={3} size={15} color="var(--color-error)" /> Inactive
                                </div>
                            )}
                        </span>
                    </div>

                    <div className={styles.infoRow}>
                        <span className={styles.label}>Role</span>
                        <span className={styles.role}>
                            {user.roles?.includes('admin') ? (
                                <div className={styles.roleAdmin}>
                                    <Shield strokeWidth={3} size={15} color='#6262f4' /> Admin
                                </div>
                            ) : (
                                <div className={styles.roleUser}>
                                    <User strokeWidth={3} size={15} color='#06065f' /> User
                                </div>
                            )}
                        </span>
                    </div>  

                    <div className={styles.infoRow}>
                        <span className={styles.label}>Created</span>
                        <span className={styles.value}>
                            {user.created_at ? new Date(user.created_at).toLocaleString() : '-'}
                        </span>
                    </div>

                    <div className={styles.infoRow}>
                        <span className={styles.label}>Last login</span>
                        <span className={styles.value}>
                            {user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}
                        </span>
                    </div>
                </div>

                <div className={styles.action}>
                    <Button className={`${styles.btn} ${styles.editBtn}`} type='button' onClick={updateUser.openModal}>
                        <Pencil strokeWidth={3} size={18}/> Edit Details                    
                    </Button>
                    {user.is_active ? (
                        <Button className={`${styles.btn} ${styles.deleteBtn}`} type='button' onClick={() => openDeleteModal(user)}>
                            <Ban strokeWidth={3} size={18}/> Delete User 
                        </Button>
                    ) : (
                        <Button className={`${styles.btn} ${styles.restoreBtn}`} type='button' onClick={() => openRestoreModal(user)}>
                            <RotateCcw strokeWidth={3} size={18}/> Restore User 
                        </Button>
                    )}
                    <Button className={`${styles.btn} ${styles.resetBtn}`} type='button'>
                        <KeyRound strokeWidth={3} size={18} /> Reset Password
                    </Button>
                </div>
            </div>

            <UserUpdateModal {...updateUser} />

            <UserConfirmModal
                confirmState={confirmModal}
                loading={actionLoading}
                error={actionError}
                onConfirm={handleConfirm}
                onClose={closeModal}
            />
        </>
    );
}