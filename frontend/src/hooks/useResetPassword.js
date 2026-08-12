import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { authService } from '@/services/authService';
import { useForm } from '@/hooks/useForm';
import { PATHS } from '@/constants/routes';

export const validateResetPassword = (values) => {
    // 1. Kiểm tra Mật khẩu mới
    if (!values.password) {
        return 'Vui lòng nhập mật khẩu mới';
    }
    if (values.password.length < 8) {
        return 'Mật khẩu phải có ít nhất 8 ký tự';
    }
    if (!/[a-z]/.test(values.password)) {
        return 'Mật khẩu phải chứa ít nhất 1 chữ cái thường (a-z)';
    }
    if (!/[A-Z]/.test(values.password)) {
        return 'Mật khẩu phải chứa ít nhất 1 chữ cái hoa (A-Z)';
    }
    if (!/[0-9]/.test(values.password)) {
        return 'Mật khẩu phải chứa ít nhất 1 chữ số (0-9)';
    }
    if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(values.password)) {
        return 'Mật khẩu phải chứa ít nhất 1 ký tự đặc biệt (!@#$%^&...)';
    }

    // 2. Kiểm tra Xác nhận mật khẩu
    if (!values.confirmPassword) {
        return 'Vui lòng xác nhận lại mật khẩu mới';
    }
    if (values.password !== values.confirmPassword) {
        return 'Mật khẩu và xác nhận mật khẩu không khớp';
    }

    return '';
};

export const useResetPassword = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token') || '';

    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    const form = useForm(
        { password: '', confirmPassword: '' },
        validateResetPassword
    );

    // Cảnh báo nếu mở URL mà không có token
    useEffect(() => {
        if (!token) {
            form.setErrorMsg('Link khôi phục mật khẩu không hợp lệ hoặc thiếu Token xác thực.');
        }
    }, [token]);

    const toggleShowPassword = () => {
        setShowPassword((prev) => !prev);
    };

    const toggleShowConfirmPassword = () => {
        setShowConfirmPassword((prev) => !prev);
    };

    const handleReset = async (formValues) => {
        if (!token) {
            form.setErrorMsg('Không tìm thấy Token xác thực. Vui lòng kiểm tra lại link trong email.');
            return;
        }

        const response = await authService.resetPassword(
            token,
            formValues.password,
            formValues.confirmPassword
        );
        const successMessage = response?.message || 'Đặt lại mật khẩu thành công!';
        
        form.setMsgSuccess(successMessage);

        // Tự động chuyển hướng về trang Đăng nhập sau 1 giây
        setTimeout(() => {
            navigate(PATHS.LOGIN);
        }, 1000);
    };

    return {
        ...form,
        showPassword,
        toggleShowPassword,
        showConfirmPassword,
        toggleShowConfirmPassword,
        onSubmit: form.handleSubmit(handleReset),
    };
};
