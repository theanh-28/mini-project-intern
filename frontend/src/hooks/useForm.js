import { useState } from 'react';

export const useForm = (initialState = {}, validateFn) => {
    const [values, setValues] = useState(initialState);
    const [errorMsg, setErrorMsg] = useState('');
    const [msgSuccess, setMsgSuccess] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Xử lý thay đổi giá trị input
    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setValues((prev) => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));

        // Xóa thông báo lỗi và thông báo thành công cũ khi người dùng nhập lại 
        if (errorMsg) setErrorMsg('');
        if (msgSuccess) setMsgSuccess('');
    };

    // Hàm xử lý submit
    const handleSubmit = (onSubmitCallback) => async (e) => {
        e.preventDefault();
        setErrorMsg('');
        setMsgSuccess('');

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
            const errData = error.response?.data?.error || error.response?.data?.detail || error.message;
            const serverError = typeof errData === 'object' 
                ? (Array.isArray(errData) ? errData[0]?.msg : errData.msg || errData.message || JSON.stringify(errData)) 
                : errData;
            setErrorMsg(serverError || 'Có lỗi xảy ra');
        } finally {
            setIsSubmitting(false);
        }
    }

    return {
        values,
        setValues,
        errorMsg,
        setErrorMsg,
        msgSuccess,
        setMsgSuccess,
        isSubmitting,
        setIsSubmitting,
        handleChange,
        handleSubmit,
    };
};