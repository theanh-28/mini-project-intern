import { useState, useEffect } from 'react';
import { useForm } from '@/hooks/useForm';
import { adminService } from '@/services/adminService';

const validateUpdate = (values) => {
    // 1. Kiểm tra rỗng
    if (!values.name?.trim()) {
        return 'Vui lòng nhập tên';
    }

    // 2. Regex kiểm tra chữ, chữ số và khoảng trắng
    const nameRegex = /^[\p{L}0-9\s]+$/u;
    if (!nameRegex.test(values.name.trim())) {
        return 'Tên chỉ chứa ký tự chữ, chữ số và khoảng trắng';
    }

    if (/\s{2,}/.test(values.name.trim())) {
        return 'Tên không được chứa hơn 1 khoảng trắng liên tiếp';
    }

    if (values.name.trim().length < 3) {
        return 'Tên phải có ít nhất 3 ký tự';
    }

    if (values.name.trim().length > 50) {
        return 'Tên tối đa 50 ký tự';
    }

    // 3. Kiểm tra Email
    if (!values.email?.trim()) return "Vui lòng nhập email";

    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(values.email.trim())) return "Định dạng email không hợp lệ (ví dụ: user@example.com)";

    return '';
};

export const useUpdateUser = ({ user, setUser }) => {
    const [isOpen, setIsOpen] = useState(false);

    // Sử dụng form chỉ với name và email
    const form = useForm({
        name: user?.name || '',
        email: user?.email || '',
    }, validateUpdate);

    const { setValues } = form;

    // Đồng bộ form values khi user data thay đổi
    useEffect(() => {
        if (user?.name) {
            setValues({
                name: user.name,
                email: user.email,
            });
        }
    }, [user, setValues]);

    const resetForm = () => {
        form.setErrorMsg('');
        form.setMsgSuccess('');
        form.setValues({
            name: user?.name || '',
            email: user?.email || '',
        });
    };

    const openModal = () => {
        resetForm();
        setIsOpen(true);
    };

    const closeModal = () => {
        setIsOpen(false);
    };

    const handleUpdate = async (userData) => {
        const isUnchanged =
            userData.name?.trim() === user?.name?.trim() &&
            userData.email?.trim() === user?.email?.trim();

        // Nếu thông tin hoàn toàn giống hệt hiện tại, không gửi request
        if (isUnchanged) {
            form.setErrorMsg('Thông tin không có sự thay đổi');
            return;
        }

        const data = await adminService.updateUser({
            userData: { name: userData.name.trim(), email: userData.email.trim() },
            userId: user.user_id,
        });

        if (setUser) {
            setUser((prev) => ({ ...prev, ...data }));
        }

        form.setMsgSuccess('Cập nhật thông tin thành công!');
        setTimeout(() => {
            closeModal();
        }, 1000);
    };

    return {
        ...form,
        isOpen,
        openModal,
        closeModal,
        resetForm,
        onSubmit: form.handleSubmit(handleUpdate),
    };
};
