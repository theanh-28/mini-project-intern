import { useState, useRef } from 'react';
import { User, LogOut, ChevronDown } from 'lucide-react';

import { useAuth } from '@/context/AuthContext';
import { useLogout } from '@/hooks/useLogout';
import { useClickOutSide } from '@/hooks/useClickOutSide';
import Avatar from '@/components/common/Avatar';
import styles from './UserMenu.module.css';

export default function UserDropdown() {
    const { user } = useAuth();
    const { handleLogout, loading } = useLogout();
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);

    useClickOutSide(dropdownRef, () => setIsOpen(false));


    return (
        <div className={styles.dropdownContainer} ref={dropdownRef}>
            <button 
                className={styles.avatarTrigger} 
                onClick={() => setIsOpen((prev) => !prev)}
                aria-label="User menu"
            >
                <div className={styles.avatarWrapper}>
                    <Avatar name={user?.name} size="sm" />
                    <span className={`${styles.badge} ${isOpen ? styles.open : ''}`}>
                        <ChevronDown size={13} strokeWidth={2.5} />
                    </span>
                </div>
            </button>

            {isOpen && (
                <div className={styles.menuPanel}>
                    <div className={styles.userInfoHeader}>
                        <Avatar name={user?.name} size="sm" />
                        <div className={styles.userDetails}>
                            <p className={styles.name}>{user?.name}</p>
                            <p className={styles.email}>{user?.email}</p>
                        </div>
                    </div>

                    <div className={styles.divider} />

                    <ul className={styles.menuList}>
                        <li className={styles.menuItem} onClick={() => setIsOpen(false)}>   
                            <User size={16} strokeWidth={2}/>
                            <span>Profile</span>
                        </li>
                        <li 
                            className={`${styles.menuItem} ${styles.logout}`} 
                            onClick={handleLogout}
                        >
                            <LogOut size={16} />
                            <span>{loading ? 'Logging out...' : 'Log out'}</span>
                        </li>
                    </ul>
                </div>
            )}
        </div>
    );
}
