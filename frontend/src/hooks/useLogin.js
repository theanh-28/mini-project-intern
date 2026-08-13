import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { PATHS } from '../constants/routes';

export const useLogin = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [errorMsg, setErrorMsg] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    const { login, loading } = useAuth();
    const navigate = useNavigate();

    const toggleShowPassword = () => {
        setShowPassword((prev) => !prev);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrorMsg('');

        if (!email || !password) {
            setErrorMsg("Vui lòng điền đầy đủ thông tin");
            return;
        }

        try {
            await login(email, password);
            navigate(PATHS.ADMIN_USERS);
        } catch (err) {
            const errMsg = err.response?.data?.error || 'Email hoặc mật khẩu không chính xác';
            setErrorMsg(errMsg);
        }
    };

    return {
        email,
        setEmail,
        password,
        setPassword,
        errorMsg,
        showPassword,
        toggleShowPassword,
        loading,
        handleSubmit,
    };
};
