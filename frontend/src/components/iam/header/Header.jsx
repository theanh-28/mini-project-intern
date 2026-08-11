import { Menu, Bell } from 'lucide-react';

import styles from './Header.module.css';
import UserMenu from '@/components/iam/header/UserMenu';

export default function Header({ collapsed, setCollapsed }) {
    return (
        <section className={styles.card}>
            <div className={styles.headerLeft}>
                <button 
                    className={styles.menuBtn}
                    onClick={() => setCollapsed(!collapsed)}
                >
                    <Menu strokeWidth={3} className={styles.menuIcon}></Menu>
                </button>
                <h1>IAM</h1>
            </div>
            <div className={styles.headerRight}>
                <Bell className={styles.bell}></Bell>
                <UserMenu />
            </div>
        </section>
    );
}