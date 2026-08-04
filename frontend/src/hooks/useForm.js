import { useState } from 'react';

export const useForm = (initialState = {}, validateFn) => {
    const [values, setValues] = useState(initialState);
    const [errorMsg, setErrorMsg] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Xử lý thay đổi giá trị input
    const handleChange = (e) => {
        const { name, value } = e.target;
        setValues((prev) => ({
            ...prev,
            [name]: value
        }));

        // Xóa lỗi khi người dùng nhập lại 
        if (errorMsg) {
            setErrorMsg('');
        }
    };

    // Hàm xử lý submit
    const handleSubmit = (onSubmitCallback) => async (e) => {
        e.preventDefault();
        setErrorMsg('');

        // Kiểm tra validation client-side
        if (validateFn) {
            const error = validateFn(values);
            if (error) {
                setErrorMsg(error);
                return;
            }
        }

        // Gọi hàm xử lý logic nghiệp vụ
        setIsSubmitting(true);
        try {
            await onSubmitCallback(values);
        } catch (error) {
            // Xử lý lỗi từ API (Server-side errors)
            const serverError = error.response?.data?.error || error.message || 'Có lỗi xảy ra';
            setErrorMsg(serverError);
        } finally {
            setIsSubmitting(false);
        }
    }

    return {
        values,
        setValues,
        errorMsg,
        setErrorMsg,
        isSubmitting,
        setIsSubmitting,
        handleChange,
        handleSubmit,
    };
};