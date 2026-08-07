import { Link, useParams } from 'react-router-dom';
import { ChevronRight, Users } from 'lucide-react';

import styles from './UserDetailPage.module.css';
import { PATHS } from '@/constants/routes';
import UserProfile from '@/components/iam/users/UserProfile';

import { useUserProfile } from '@/hooks/useUserProfile';


export default function UserDetailPage() {
    const { userId } = useParams();
    const userProfile = useUserProfile(userId);
    const user = userProfile.user;

    return (
        <>
            <div className={styles.page}>
                <section className={styles.header}>
                    <div className={styles.title}>
                        {user?.name}
                    </div>
                    <div className={styles.navigate}>
                        <Link to={PATHS.ADMIN_USERS} className={styles.linkUsers}>
                            <Users strokeWidth='2' size='15'/>
                            Users
                        </Link>
                        <ChevronRight strokeWidth='2' size='15' color='var(--color-text-muted)'/>
                        {user?.name}
                    </div>
                </section>

                <section className={styles.userProfile}>
                    <UserProfile {...userProfile}/>
                </section>
            </div>
        </>
    );
}