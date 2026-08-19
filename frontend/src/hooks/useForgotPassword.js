import { useState, useEffect, useCallback } from 'react';
import { authService } from '@/services/authService';
import { useForm } from '@/hooks/useForm';

const COOLDOWN_TIME = 30; // 30 giây đếm ngược giới hạn resend
const STORAGE_KEY = 'forgot_password_cooldowns';

// Đọc và dọn dẹp các email đã hết hạn trong localStorage map
const getCooldownMap = () => {
    try {
        const item = localStorage.getItem(STORAGE_KEY);
        if (!item) return {};
        const map = JSON.parse(item);

        const now = Date.now();
        const cleanMap = {};
        let changed = false;

        Object.keys(map).forEach((emailKey) => {
            if (map[emailKey] > now) {
                cleanMap[emailKey] = map[emailKey];
            } else {
                changed = true;
            }
        });

        if (changed) {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(cleanMap));
        }
        return cleanMap;
    } catch {
        localStorage.removeItem(STORAGE_KEY);
        return {};
    }
};

// Lấy mốc expiresAt của một email cụ thể
const getEmailExpiresAt = (email) => {
    if (!email) return null;
    const cleanEmail = email.trim().toLowerCase();
    const map = getCooldownMap();
    return map[cleanEmail] || null;
};

// Lưu mốc expiresAt cho một email cụ thể
const saveEmailCooldown = (email, expiresAt) => {
    if (!email) return;
    const cleanEmail = email.trim().toLowerCase();
    const map = getCooldownMap();
    map[cleanEmail] = expiresAt;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(map));
};

const validateForgotPassword = (values) => {
    if (!values.email?.trim()) {
        return 'Vui lòng nhập email';
    }
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(values.email.trim())) {
        return 'Định dạng email không hợp lệ (ví dụ: user@example.com)';
    }

    return '';
};

export const useForgotPassword = () => {
    const form = useForm({ email: '' }, validateForgotPassword);
    const { values } = form;

    const currentEmail = values.email?.trim()?.toLowerCase() || '';

    const [expiresAt, setExpiresAt] = useState(() => getEmailExpiresAt(currentEmail));
    const [countdown, setCountdown] = useState(0);

    // Cập nhật mốc đếm ngược khi người dùng gõ/thay đổi email
    useEffect(() => {
        const exp = getEmailExpiresAt(currentEmail);
        setExpiresAt(exp);

        if (exp && exp > Date.now()) {
            form.setMsgSuccess('Link khôi phục mật khẩu đã được gửi đến email của bạn. Vui lòng kiểm tra hộp thư!');
        } else {
            form.setMsgSuccess('');
        }
    }, [currentEmail]);

    // Tính toán số giây còn lại cho email hiện tại
    const updateCountdown = useCallback(() => {
        if (!expiresAt) {
            setCountdown(0);
            return;
        }

        const remaining = Math.ceil((expiresAt - Date.now()) / 1000);
        if (remaining <= 0) {
            setCountdown(0);
            setExpiresAt(null);
            getCooldownMap();
        } else {
            setCountdown(remaining);
        }
    }, [expiresAt]);

    // Tự động đồng bộ số giây còn lại + bắt sự kiện chuyển tab (visibilitychange)
    useEffect(() => {
        if (!expiresAt) {
            setCountdown(0);
            return;
        }

        updateCountdown();
        const timer = setInterval(updateCountdown, 1000);

        const handleVisibilityChange = () => {
            if (document.visibilityState === 'visible') {
                updateCountdown();
            }
        };

        document.addEventListener('visibilitychange', handleVisibilityChange);

        return () => {
            clearInterval(timer);
            document.removeEventListener('visibilitychange', handleVisibilityChange);
        };
    }, [expiresAt, updateCountdown]);

    const handleSendRequest = async (formValues) => {
        const email = formValues.email.trim().toLowerCase();

        // Kiểm tra cooldown riêng của email này
        const currentExp = getEmailExpiresAt(email);
        if (currentExp && currentExp > Date.now()) return;

        const data = await authService.forgotPassword(email);
        const successMessage = data?.message || 'Link khôi phục mật khẩu đã được gửi đến email của bạn. Vui lòng kiểm tra hộp thư!';
        form.setMsgSuccess(successMessage);

        // Lưu mốc hết hạn cho ĐÚNG email này
        const newExpiresAt = Date.now() + COOLDOWN_TIME * 1000;
        saveEmailCooldown(email, newExpiresAt);
        setExpiresAt(newExpiresAt);
    };

    return {
        ...form,
        countdown,
        isCooldown: countdown > 0,
        onSubmit: form.handleSubmit(handleSendRequest),
    };
};
