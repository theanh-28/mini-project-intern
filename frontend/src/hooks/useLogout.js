import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { useAuth } from '@/context/AuthContext';
import { PATHS } from '@/constants/routes';

export const useLogout = () => {
    const [loading, setLoading] = useState(false);
    const { logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        setLoading(true);

        try {
            await logout();
        } catch (err) {
            console.error('Lỗi khi đăng xuất: ', err);
        } finally {
            navigate(PATHS.LOGIN);
        }
    }

    return {
        loading,
        handleLogout,
    }
}