import { Link, useParams, useNavigate } from 'react-router-dom';
import { ChevronRight, Users } from 'lucide-react';

import styles from './UserDetailPage.module.css';
import { PATHS } from '@/constants/routes';
import UserProfile from '@/components/iam/users/UserProfile';
import UserIntegrations from '@/components/iam/users/UserIntegrations';

import { useUserProfile } from '@/hooks/useUserProfile';


export default function UserDetailPage() {
    const { userId } = useParams();
    const navigate = useNavigate();
    const userProfile = useUserProfile(userId);
    const user = userProfile.user;

    const handleDeleteSuccess = () => {
        navigate(PATHS.ADMIN_USERS);
    };

    return (
        <div className={styles.page}>
            <section className={styles.header}>
                <div className={styles.title}>
                    {user?.name || 'User Profile'}
                </div>
                <div className={styles.navigate}>
                    <Link to={PATHS.ADMIN_USERS} className={styles.linkUsers}>
                        <Users strokeWidth='2' size='15'/>
                        Users
                    </Link>
                    <ChevronRight strokeWidth='2' size='15' color='var(--color-text-muted)'/>
                    {user?.name || 'User Profile'}
                </div>
            </section>

            <div className={styles.layout}>
                <section className={styles.leftCol}>
                    <UserProfile {...userProfile} onDeleteSuccess={handleDeleteSuccess} />
                </section>
                <section className={styles.rightCol}>
                    <UserIntegrations user={user} />
                </section>
            </div>
        </div>
    );
}