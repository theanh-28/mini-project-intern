import styles from './UserTable.module.css';
import Spinner from '@/components/common/Spinner';
import Button from '@/components/common/Button';
import { CircleCheck, Ban, Shield, User, Trash2, RotateCcw } from 'lucide-react';
import { useUserActions } from '@/hooks/useUserActions';
import UserConfirmModal from '@/components/iam/users/UserConfirmModal';
import { Link } from 'react-router-dom';
import { PATHS } from '@/constants/routes';

export default function UserTable({ users, loading, error, page}) {
    const {
        confirmModal,
        loading: actionLoading,
        error: actionError,
        openDeleteModal,
        openRestoreModal,
        closeModal,
        handleConfirm,
    } = useUserActions();

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
                                {user.roles?.includes('admin') ? (
                                    <div className={styles.roleAdmin}>
                                        <Shield strokeWidth={3} size={15} color='#6262f4' /> Admin
                                    </div>
                                ) : (
                                    <div className={styles.roleUser}>
                                        <User strokeWidth={3} size={15} color='#06065f' /> User
                                    </div>
                                )}
                            </td>
                            <td>{new Date(user.created_at).toLocaleDateString()}</td>
                            <td>{user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}</td>
                            <td className={styles.action}>
                                {user.is_active ? (
                                    <Button className={styles.delete} onClick={() => openDeleteModal(user)}>
                                        <Trash2 strokeWidth={3} size={15} color='#fff' /> Delete
                                    </Button>
                                ) : (
                                    <Button className={styles.restore} onClick={() => openRestoreModal(user)}>
                                        <RotateCcw strokeWidth={3} size={15} color='#fff' /> Restore
                                    </Button>
                                )}
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