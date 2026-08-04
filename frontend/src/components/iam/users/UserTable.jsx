import styles from './UserTable.module.css';
import Spinner from '@/components/common/Spinner';
import Button from '@/components/common/Button'
import { CircleCheck, Ban, Shield, User, X } from 'lucide-react';

export default function UserTable({ users, loading, error, page }) {
    return (
        <table className={styles.table}>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Name</th>
                    <th>active</th>
                    <th>Role</th>
                    <th>Created At</th>
                    <th>Last Login</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {loading ? (
                    <tr >
                        <td colSpan="7">
                            <Spinner />
                        </td>
                    </tr>
                ) : error ? (
                    <tr>
                        <td colSpan="7">
                            <div className={styles.error}>Error loading users: {error.message}</div>
                        </td>
                    </tr>
                ) : (users || []).map((user, index) => (
                    <tr key={user.user_id} className={user.is_active ? '' : styles.inactive}>
                        <td>{page ? (page - 1) * 20 + (index + 1) : page * 20 + (index + 1)}</td>
                        <td>{user.name}</td>
                        <td className={styles.active}>
                            {user.is_active ?
                                (<div className={styles.statusActive}><CircleCheck strokeWidth={3} size={15} color='var(--color-success)' /> active</div>)
                                : (<div className={styles.statusInactive}><Ban strokeWidth={3} size={15} color="var(--color-error)" /> inactive</div>)}
                        </td>
                        <td className={styles.role}>
                            {user.is_admin ? (
                                <div className={styles.roleAdmin}><Shield strokeWidth={3} size={15} color='#6262f4' /> Admin</div>
                            ) : (
                                <div className={styles.roleUser}><User strokeWidth={3} size={15} color='#06065f' /> User</div>
                            )}
                        </td>
                        <td>{new Date(user.created_at).toLocaleDateString()}</td>
                        <td>{user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}</td>
                        <td><Button className={styles.delete} ><X strokeWidth={3} size={15} /> delete</Button></td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
}