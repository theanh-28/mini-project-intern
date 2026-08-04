import { useNavigate } from 'react-router-dom';
import { Users, Plus } from 'lucide-react';

import { useAuth } from '@/context/AuthContext';
import { PATHS } from '@/constants/routes';
import styles from './UsersPage.module.css';

import UserTable from '@/components/iam/users/UserTable';
import UserCreateModal from '@/components/iam/users/UserCreateModal';
import Pagination from '@/components/iam/users/Pagination';
import Button from '@/components/common/Button';

import { useUsersTable } from '@/hooks/useUsersTable';
import { useCreateUser } from '@/hooks/useCreateUser';

export default function UsersPage() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const { users, page, handlePageInputChange, handleBlur, totalPages, loading, error, total, fetchUsers } = useUsersTable();
    const {
        showPassword,
        toggleShowPassword,
        showConfirmPassword,
        toggleShowConfirmPassword,
        showModal,
        setShowModal,
        msgSuccess,
        onSubmit,
        resetForm,
        ...form
    } = useCreateUser(fetchUsers);

    return (
        <section className={styles.card}>
            <div className={styles.header}>
                <div className={styles.headerLeft}>
                    <Users size='24' strokeWidth='3' /> <span className={styles.title}>Users ({total})</span>
                </div>

                <Button
                    className={styles.createUser}
                    onClick={() => setShowModal(true)}
                >
                    <Plus size='18' strokeWidth='5' /> <span style={{ fontSize: '1rem', fontWeight: 300 }}>Add user</span>
                </Button>
            </div>

            <div className={styles.content}>
                <div className={styles.table}>
                    <UserTable users={users} loading={loading} error={error} page={page} />
                </div>
                <div className={styles.footer}>
                    <Pagination
                        currentPage={page}
                        totalPages={totalPages}
                        onPageChange={handlePageInputChange}
                        onBlur={handleBlur}
                    />
                </div>
            </div>
            <UserCreateModal
                open={showModal}
                setShowModal={setShowModal}
                onSubmit={onSubmit}
                values={form.values}
                onChange={form.handleChange}
                showPassword={showPassword}
                toggleShowPassword={toggleShowPassword}
                showConfirmPassword={showConfirmPassword}
                toggleShowConfirmPassword={toggleShowConfirmPassword}
                msgSuccess={msgSuccess}
                errorMsg={form.errorMsg}
                resetForm={resetForm}
                isSubmitting={form.isSubmitting}
            />
        </section>
    );
}
