import { createContext, useState, useEffect, useContext } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Kiểm tra token JWT đã hết hạn chưa
    const isTokenExpired = (token) => {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return payload.exp * 1000 < Date.now();
        } catch {
            return true; // Token sai format => coi như hết hạn
        }
    };

    // Khi ứng dụng khởi động phục hồi phiên đăng nhập từ localStorage
    useEffect(() => {
        const token = localStorage.getItem('token');
        const savedUser = localStorage.getItem('user');

        if (token && savedUser && !isTokenExpired(token)) {
            setUser(JSON.parse(savedUser));
        } else {
            // Token không có, hết hạn, hoặc sai format
            localStorage.removeItem('token');
            localStorage.removeItem('user');
        }
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        setLoading(true);
        try {
            const data = await authService.login(email, password);
            // Lưu token và thông tin user vào localStorage
            localStorage.setItem('token', data.access_token);
            
            const loggedUser = {
                user_id: data.user.user_id,
                email: data.user.email || email,
                name: data.user.name,
                is_admin: data.user.is_admin,
            };
            localStorage.setItem('user', JSON.stringify(loggedUser));
            setUser(loggedUser);
            return loggedUser;
        } catch (error) {
            throw error;
        } finally {
            setLoading(false);
        }
    };

    const logout = async () => {
        try {
            await authService.logout();
        } catch (e) {
            console.error("Lỗi gọi API logout: ", e);
        } finally {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            setUser(null);
        }
    };

    return (
        <AuthContext.Provider value={{user, loading, login, logout}}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext)