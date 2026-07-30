import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { EyeOff, Eye } from 'lucide-react';

import { useAuth } from '../../context/AuthContext';
import styles from './LoginPage.module.css';

const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [errorMsg, setErrorMsg] = useState('');
    const { login, loading } = useAuth();
    const [showPassword, setShowPassword] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrorMsg('');

        if (!email || !password) {
            setErrorMsg("Vui lòng điền đầy đủ thông tin");
            return;
        }

        try {
            const user = await login(email, password);
            // Đăng nhập thành công, điều hướng 
            navigate('/admin/users');
        } catch (err) {
            // Lấy thông tin lỗi
            const errMsg = err.response?.data?.error || 'Email hoặc mật khẩu không chính xác';
            setErrorMsg(errMsg);
        }
    };

    return (
        <section className={styles.card}>
            <div className={styles.header}>
                <h2>Đăng nhập</h2>
            </div>

            <form onSubmit={handleSubmit} className={styles.form} noValidate>
                <div className={styles.inputGroup}>
                    <label htmlFor='email'>Email</label>
                    <input
                        type='email'
                        id='email'
                        placeholder='abc@example.com'
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        disabled={loading}
                        required
                    />
                </div>

                <div className={styles.inputGroup}>
                    <label htmlFor='password'>Password</label>
                    <div className={styles.passwordWrapper}>
                        <input
                            type={showPassword ? 'text' : 'password'}
                            id='password'
                            placeholder='*********'
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            disabled={loading}
                            required
                        />
                        <button 
                            className={styles.toggleBtn} 
                            type='button' 
                            onClick={() => setShowPassword((prev) => !prev)}
                            tabIndex={-1} // Không cho tab dừng lại ở icon này
                        >
                            {showPassword ? <EyeOff size={18}/> : <Eye size={18}/>}
                        </button>
                    </div>
                </div>

                {errorMsg && (
                    <div className={styles.errorMsg}>
                        {errorMsg}
                    </div>
                )}

                <div className={styles.forgotLink}>
                    <Link to='/auth/forgot-password'>Quên mật khẩu</Link>
                </div>

                <button type='submit' className={styles.btnSubmit} disabled={loading}>
                    {loading ? <span className={styles.spinner}></span> : 'Đăng Nhập'}
                </button>
            </form>
        </section>
    )
};

export default LoginPage;