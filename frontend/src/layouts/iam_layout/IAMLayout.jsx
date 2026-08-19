import { Outlet } from 'react-router-dom';
import { useState} from 'react';
import clsx from 'clsx';

import styles from './IAMLayout.module.css';
import Sidebar from '@/components/iam/sidebar/Sidebar';
import Header from '@/components/iam/header/Header'

export default function IAMLayout() {
    const [collapsed, setCollapsed] = useState(false);

    return (
        <div className={styles.layout}>
            <header className={styles.header}>
                <Header collapsed={collapsed} setCollapsed={setCollapsed} />
            </header>
            <div className={styles.wrapper}>
                <aside 
                    className={clsx(
                        styles.sidebar,
                        collapsed && styles.collapsed,
                    )}
                >
                    <Sidebar collapsed={collapsed} />
                </aside>
                <main className={styles.main}>
                    <Outlet />
                </main>
            </div>
        </div>
    )
}