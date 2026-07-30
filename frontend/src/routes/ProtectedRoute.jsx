import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ requireAdmin = false }) => {
    const { user, loading } = useAuth();

    if (loading) return <div>Đang tải...</div>;
    
    if (!user) {
        // Chưa đăng nhập thì điều hướng về trang đăng nhập
        return <Navigate to='/auth/login' replace />;
    }

    if (requireAdmin && !user.is_admin) {
        // Nếu trang yêu cầu admin nhưng user thường thì trả về trang cấm truy cập /403
        return <Navigate to='/403' replace />;
    }

    return <Outlet />;
}

export default ProtectedRoute;