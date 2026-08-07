import { Users, Plus } from 'lucide-react';
import styles from './UsersPage.module.css';

import UserTable from '@/components/iam/users/UserTable';
import UserCreateModal from '@/components/iam/users/UserCreateModal';
import Pagination from '@/components/iam/users/Pagination';
import Button from '@/components/common/Button';

import { useUsersTable } from '@/hooks/useUsersTable';
import { useCreateUser } from '@/hooks/useCreateUser';

export default function UsersPage() {
    const usersTable = useUsersTable();
    const createUserModal = useCreateUser(usersTable.fetchUsers);

    return (
        <section className={styles.card}>
            <div className={styles.header}>
                <div className={styles.headerLeft}>
                    <Users size='24' strokeWidth='3' /> <span className={styles.title}>Users ({usersTable.total})</span>
                </div>

                <Button
                    className={styles.createUser}
                    onClick={createUserModal.openModal}
                >
                    <Plus size='18' strokeWidth='5' /> <span style={{ fontSize: '1rem', fontWeight: 300 }}>Add user</span>
                </Button>
            </div>

            <div className={styles.content}>
                <div className={styles.table}>
                    <UserTable 
                        users={usersTable.users} 
                        loading={usersTable.loading} 
                        error={usersTable.error} 
                        page={usersTable.page} 
                    />
                </div>
                <div className={styles.footer}>
                    <Pagination
                        currentPage={usersTable.page}
                        totalPages={usersTable.totalPages}
                        onPageChange={usersTable.handlePageInputChange}
                        onBlur={usersTable.handleBlur}
                    />
                </div>
            </div>

            <UserCreateModal {...createUserModal} />
        </section>
    );
}
