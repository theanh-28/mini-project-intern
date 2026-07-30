import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function UsersPage() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();
        navigate('/auth/login');
    };

    return (
        <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
            <h1>Admin Page</h1>
            <p>Xin chào, {user?.name || 'Admin'} ({user?.email})!</p>
            <button onClick={handleLogout} style={{ padding: '0.5rem 1rem', cursor: 'pointer', marginTop: '1rem' }}>
                Đăng xuất
            </button>
        </div>
    );
}
