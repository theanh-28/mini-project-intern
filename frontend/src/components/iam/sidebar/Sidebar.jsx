import { House, Users, BookText, ClipboardList} from 'lucide-react'
import { Link } from 'react-router-dom';

import styles from './Sidebar.module.css';
import Avatar from '@/components/common/Avatar';
import { useAuth } from '@/context/AuthContext';
import { PATHS } from '@/constants/routes';

export default function Sidebar() {
    const {user} = useAuth();
    return (
        <section className={styles.card}>
            <div className={styles.userInfo}>
                <Avatar name={user.name} size='md'></Avatar>
                <span className={styles.userName}>
                    {user.name}
                </span>
            </div>
            <div className={styles.menuSection}>
                <h3 className={styles.sectionTitle}>
                    Organization Management
                </h3>

                <ul className={styles.menuList}>

                    <li className={styles.menuItem}>
                        <Link className={styles.menuLink}>
                            <House /> Home
                        </Link>
                    </li>

                    <li className={styles.menuItem}>
                        <Link to={PATHS.ADMIN_USERS} className={styles.menuLink}>
                            <Users /> Users
                        </Link>
                    </li>

                    <li className={styles.menuItem}>
                        <Link className={styles.menuLink}>
                            <ClipboardList /> Requests
                        </Link>
                    </li>

                    <li className={styles.menuItem}>
                        <Link className={styles.menuLink}>
                            <BookText /> AUP
                        </Link>
                    </li>

                </ul>
            </div>
        </section>
    );
}