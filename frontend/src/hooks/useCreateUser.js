import { useState, useEffect } from 'react';
import { adminService } from '@/services/adminService';

import { useForm } from '@/hooks/useForm';

const validateCreateUser = (values) => {
    // 1. Kiểm tra Username
    if (!values.name?.trim()) {
        return "Vui lòng nhập tên người dùng";
    }
    if (values.name.trim().length < 3) {
        return "Tên người dùng phải có ít nhất 3 ký tự";
    }

    // 2. Kiểm tra Email
    if (!values.email?.trim()) {
        return "Vui lòng nhập email";
    }
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(values.email.trim())) {
        return "Định dạng email không hợp lệ (ví dụ: user@example.com)";
    }

    // 3. Kiểm tra Mật khẩu
    if (!values.password) {
        return "Vui lòng nhập mật khẩu";
    }
    if (values.password.length < 6) {
        return "Mật khẩu phải có ít nhất 6 ký tự";
    }

    // 4. Kiểm tra Xác nhận mật khẩu
    if (!values.confirmPassword) {
        return "Vui lòng xác nhận lại mật khẩu";
    }
    if (values.password !== values.confirmPassword) {
        return "Mật khẩu và xác nhận mật khẩu không khớp";
    }

    return '';
};

export const useCreateUser = (onSuccess) => {
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [showModal, setShowModal] = useState(false);
    const [msgSuccess, setMsgSuccess] = useState('');

    const form = useForm({
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
    }, validateCreateUser);

    const toggleShowPassword = () => {
        setShowPassword((prev) => !prev);
    };

    const toggleShowConfirmPassword = () => {
        setShowConfirmPassword((prev) => !prev);
    };

    const resetForm = () => {
        setShowPassword(false);
        setShowConfirmPassword(false);
        setMsgSuccess('');
        form.setErrorMsg('');
        form.setValues({ name: '', email: '', password: '', confirmPassword: '' });
    };

    const handleCreateUser = async (formValues) => {
        setMsgSuccess('');
        
        await adminService.createUser(formValues);
        form.setValues({ name: '', email: '', password: '', confirmPassword: '' });
        setMsgSuccess('Người dùng đã được tạo thành công!');
        if (onSuccess) {
            onSuccess();
        }
    };

    return { 
        ...form, 
        onSubmit: form.handleSubmit(handleCreateUser),
        showPassword, 
        toggleShowPassword, 
        showConfirmPassword, 
        toggleShowConfirmPassword, 
        showModal, 
        setShowModal,
        msgSuccess,
        resetForm,
    };
};