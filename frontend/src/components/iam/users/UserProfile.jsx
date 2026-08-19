import { 
    User, 
    Shield, 
    CircleCheck, 
    Ban, 
    Pencil, 
    KeyRound, 
    Trash2 
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
    fetchUser,
    onRefresh = fetchUser,
    onDeleteSuccess,
}) {
    const updateUser = useUpdateUser({ user, setUser });

    const {
        confirmModal,
        loading: actionLoading,
        error: actionError,
        successMsg,
        resetPasswordLoading,
        actionFeedback,
        openDeleteModal,
        openStatusModal,
        openResetPasswordModal,
        closeModal,
        handleConfirm,
        handleResetPassword,
    } = useUserActions({ 
        onRefresh: onRefresh || fetchUser, 
        onUserUpdate: setUser,
        onDeleteSuccess,
    });

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
                        ID: {user.user_id}
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
                            <div className={styles.rolesContainer}>
                                {user.roles && user.roles.length > 0 ? (
                                    user.roles.map((role) => (
                                        <div
                                            key={role}
                                            className={role === 'admin' ? styles.roleAdmin : styles.roleItem}
                                        >
                                            {role === 'admin' ? (
                                                <Shield strokeWidth={2.5} size={14} color='#6262f4' />
                                            ) : (
                                                <User strokeWidth={2.5} size={14} color='#06065f' />
                                            )}
                                            <span>{role.charAt(0).toUpperCase() + role.slice(1)}</span>
                                        </div>
                                    ))
                                ) : (
                                    <span className={styles.noRole}>-</span>
                                )}
                            </div>
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

                {/* Phản hồi thao tác (thành công hoặc lỗi) */}
                {actionFeedback.msg && (
                    <div className={actionFeedback.type === 'success' ? styles.feedbackSuccess : styles.feedbackError}>
                        {actionFeedback.msg}
                    </div>
                )}

                {actionError && (
                    <div className={styles.feedbackError}>
                        {actionError}
                    </div>
                )}

                <div className={styles.action}>
                    {/* Action 1: Chỉnh sửa thông tin cơ bản (Name, Email) */}
                    <Button 
                        className={`${styles.btn} ${styles.editBtn}`} 
                        type='button' 
                        onClick={updateUser.openModal}
                    >
                        <Pencil strokeWidth={2.5} size={18}/> Edit Details                    
                    </Button>

                    {/* Action 2: Bật / Tắt trạng thái hoạt động (is_active) */}
                    {user.is_active ? (
                        <Button 
                            className={`${styles.btn} ${styles.deactivateBtn}`} 
                            type='button' 
                            onClick={() => openStatusModal(user)}
                        >
                            <Ban strokeWidth={2.5} size={18}/> Deactivate Account
                        </Button>
                    ) : (
                        <Button 
                            className={`${styles.btn} ${styles.activateBtn}`} 
                            type='button' 
                            onClick={() => openStatusModal(user)}
                        >
                            <CircleCheck strokeWidth={2.5} size={18}/> Activate Account
                        </Button>
                    )}

                    {/* Action 3: Gửi yêu cầu đặt lại mật khẩu */}
                    <Button 
                        className={`${styles.btn} ${styles.resetBtn}`} 
                        type='button'
                        onClick={() => openResetPasswordModal(user)}
                        isLoading={resetPasswordLoading}
                    >
                        <KeyRound strokeWidth={2.5} size={18} /> Reset Password
                    </Button>

                    {/* Action 4: Xóa mềm tài khoản */}
                    <Button 
                        className={`${styles.btn} ${styles.deleteBtn}`} 
                        type='button' 
                        onClick={() => openDeleteModal(user)}
                    >
                        <Trash2 strokeWidth={2.5} size={18}/> Delete User 
                    </Button>
                </div>
            </div>

            <UserUpdateModal {...updateUser} />

            <UserConfirmModal
                confirmState={confirmModal}
                loading={actionLoading}
                error={actionError}
                successMsg={successMsg}
                onConfirm={handleConfirm}
                onClose={closeModal}
            />
        </>
    );
}