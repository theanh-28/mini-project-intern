import { Outlet } from 'react-router-dom';

import styles from './IAMLayout.module.css';
import Sidebar from '@/components/iam/sidebar/Sidebar';
import Header from '@/components/iam/header/Header'

export default function IAMLayout() {
    return (
        <div className={styles.layout}>
            <header className={styles.header}>
                <Header />
            </header>
            <div className={styles.wrapper}>
                <aside className={styles.sidebar}>
                    <Sidebar />
                </aside>
                <main className={styles.main}>
                    <Outlet />
                </main>
            </div>
        </div>
    )
}