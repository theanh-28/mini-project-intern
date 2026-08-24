import { House, Users, History, GitPullRequest, FileCheck } from 'lucide-react';
import { Link } from 'react-router-dom';
import clsx from 'clsx';

import styles from './Sidebar.module.css';
import Avatar from '@/components/common/Avatar';
import { useAuth } from '@/context/AuthContext';
import { PATHS } from '@/constants/routes';

const MENU_ITEMS = [
    { icon: House, label: 'Home', path: PATHS.HOME },
    { icon: Users, label: 'Users', path: PATHS.ADMIN_USERS },
    { icon: History, label: 'Audit Logs', path: PATHS.ADMIN_AUDIT_LOGS },
    { icon: FileCheck, label: 'AUP', path: PATHS.AUP },
];

export default function Sidebar({ collapsed }) {
    const { user } = useAuth();

    return (
        <section className={clsx(styles.card, collapsed && styles.collapsed)}>
            <div className={styles.userInfo}>
                <Avatar name={user?.name} size="md" style={{ cursor: 'default' }} />
                <span className={styles.userName}>{user?.name}</span>
            </div>

            <div className={styles.menuSection}>
                <h3 className={styles.sectionTitle}>
                    <span className={styles.sectionTitleText}>
                        Organization Management
                    </span>
                </h3>

                <ul className={styles.menuList}>
                    {MENU_ITEMS.map(({ icon: Icon, label, path }) => (
                        <li
                            key={path}
                            className={styles.menuItem}
                            title={collapsed ? label : undefined}
                        >
                            <Link to={path} className={styles.menuLink}>
                                <span className={styles.menuIcon}><Icon /></span>
                                <span className={styles.menuLabel}>{label}</span>
                            </Link>
                        </li>
                    ))}
                </ul>
            </div>
        </section>
    );
}