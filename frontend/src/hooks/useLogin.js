import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { PATHS } from '@/constants/routes';
import { useForm } from '@/hooks/useForm';

const validateLogin = (values) => {
    // 1. Kiểm tra Email
    if (!values.email?.trim()) {
        return "Vui lòng nhập email";
    }
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(values.email.trim())) {
        return "Định dạng email không hợp lệ (ví dụ: user@example.com)";
    }

    // 2. Kiểm tra Mật khẩu
    if (!values.password) {
        return "Vui lòng nhập mật khẩu";
    }
    if (values.password.length < 6) {
        return "Mật khẩu phải có ít nhất 6 ký tự";
    }

    return '';
};

export const useLogin = () => {
    const [showPassword, setShowPassword] = useState(false);
    const { login, user } = useAuth();
    const navigate = useNavigate();

    // Nếu người dùng đã đăng nhập từ trước và là admin, tự động chuyển hướng sang trang admin/users
    useEffect(() => {
        if (user) {
            const isAdmin = user.roles?.includes('admin');
            if (isAdmin) {
                navigate(PATHS.ADMIN_USERS, { replace: true });
            }
        }
    }, [user, navigate]);

    // Sử dụng useForm 
    const form = useForm(
        { email: '', password: '' },
        validateLogin,
    );

    const toggleShowPassword = () => {
        setShowPassword((prev) => !prev);
    };

    const handleLogin = async (formValues) => {
        await login(
            formValues.email,
            formValues.password,
        );
        navigate(PATHS.ADMIN_USERS, { replace: true });
    };

    return {
        ...form,
        showPassword,
        toggleShowPassword,
        onSubmit: form.handleSubmit(handleLogin),
    };
};
