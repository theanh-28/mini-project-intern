import styles from './UserTable.module.css';
import Spinner from '@/components/common/Spinner';
import Button from '@/components/common/Button';
import { CircleCheck, Ban, Shield, User, Trash2 } from 'lucide-react';
import { useUserActions } from '@/hooks/useUserActions';
import UserConfirmModal from '@/components/iam/users/UserConfirmModal';
import { Link } from 'react-router-dom';
import { PATHS } from '@/constants/routes';

export default function UserTable({ users, loading, error, page, onRefresh }) {
    const {
        confirmModal,
        loading: actionLoading,
        error: actionError,
        statusLoadingId,
        openDeleteModal,
        openStatusModal,
        closeModal,
        handleConfirm,
    } = useUserActions({ onRefresh });

    return (
        <>
            <table className={styles.table}>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Name</th>
                        <th>Status</th>
                        <th>Role</th>
                        <th>Created At</th>
                        <th>Last Login</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {loading ? (
                        <tr>
                            <td colSpan="7">
                                <Spinner />
                            </td>
                        </tr>
                    ) : error ? (
                        <tr>
                            <td colSpan="7">
                                <div className={styles.error}>Error loading users: {error}</div>
                            </td>
                        </tr>
                    ) : (users || []).map((user, index) => (
                        <tr key={user.user_id} className={user.is_active ? '' : styles.inactive}>
                            <td>{page ? (page - 1) * 20 + (index + 1) : (index + 1)}</td>
                            <td className={styles.userName}>
                                <Link to={`${PATHS.ADMIN_USERS}/${user.user_id}`}>
                                     {user.name}
                                </Link>
                            </td>
                            <td className={styles.status}>
                                {user.is_active ? (
                                    <div className={styles.statusActive}>
                                        <CircleCheck strokeWidth={3} size={15} color='var(--color-success)' /> Active
                                    </div>
                                ) : (
                                    <div className={styles.statusInactive}>
                                        <Ban strokeWidth={3} size={15} color="var(--color-error)" /> Inactive
                                    </div>
                                )}
                            </td>
                            <td className={styles.role}>
                                <div className={styles.rolesContainer}>
                                    {user.roles && user.roles.length > 0 ? (
                                        user.roles.map((role) => (
                                            <div
                                                key={role}
                                                className={role === 'admin' ? styles.roleAdmin : styles.roleItem}
                                            >
                                                {role === 'admin' ? (
                                                    <Shield strokeWidth={2.5} size={13} color='#6262f4' />
                                                ) : (
                                                    <User strokeWidth={2.5} size={13} color='#06065f' />
                                                )}
                                                <span>{role.charAt(0).toUpperCase() + role.slice(1)}</span>
                                            </div>
                                        ))
                                    ) : (
                                        <span className={styles.noRole}>-</span>
                                    )}
                                </div>
                            </td>
                            <td>{new Date(user.created_at).toLocaleDateString()}</td>
                            <td>{user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}</td>
                            <td className={styles.action}>
                                <div className={styles.actionGroup}>
                                    {/* Action 1: Toggle Status is_active */}
                                    {user.is_active ? (
                                        <Button
                                            className={styles.toggleDeactivate}
                                            onClick={() => openStatusModal(user)}
                                            disabled={statusLoadingId === user.user_id}
                                            title="Deactivate account"
                                        >
                                            <Ban strokeWidth={2.5} size={14} /> Deactivate
                                        </Button>
                                    ) : (
                                        <Button
                                            className={styles.toggleActivate}
                                            onClick={() => openStatusModal(user)}
                                            disabled={statusLoadingId === user.user_id}
                                            title="Activate account"
                                        >
                                            <CircleCheck strokeWidth={2.5} size={14} /> Activate
                                        </Button>
                                    )}

                                    {/* Action 2: Soft Delete User */}
                                    <Button
                                        className={styles.delete}
                                        onClick={() => openDeleteModal(user)}
                                        title="Delete user"
                                    >
                                        <Trash2 strokeWidth={2.5} size={14} /> Delete
                                    </Button>
                                </div>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

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