import { Menu, Bell, User } from 'lucide-react';

import styles from './Header.module.css';
import { useAuth } from '@/context/AuthContext';
import Avatar from '@/components/common/Avatar';

export default function Header() {
    const { user } = useAuth();

    return (
        <section className={styles.card}>
            <div className={styles.headerLeft}>
                <Menu className={styles.menu}></Menu>
                <h1>IAM</h1>
            </div>
            <div className={styles.headerRight}>
                <Bell className={styles.bell}></Bell>
                <Avatar name={user.name} size='sm'></Avatar>
                <span className={styles.userName}>
                    {user.name}
                </span>
            </div>
        </section>
    );
}