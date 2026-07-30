import { Link } from 'react-router-dom';
import { EyeOff, Eye } from 'lucide-react';

import { useLogin } from '../../hooks/useLogin';
import { PATHS } from '../../constants/routes';
import Input from '../../components/common/Input';
import Button from '../../components/common/Button';
import styles from './LoginPage.module.css';

const LoginPage = () => {
    const {
        email,
        setEmail,
        password,
        setPassword,
        errorMsg,
        showPassword,
        toggleShowPassword,
        loading,
        handleSubmit,
    } = useLogin();

    return (
        <section className={styles.card}>
            <div className={styles.header}>
                <h2>Đăng nhập</h2>
            </div>

            <form onSubmit={handleSubmit} className={styles.form} noValidate>
                <Input
                    label="Email"
                    type="email"
                    id="email"
                    placeholder="abc@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={loading}
                    required
                />

                <Input
                    label="Password"
                    type={showPassword ? 'text' : 'password'}
                    id="password"
                    placeholder="*********"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={loading}
                    required
                    style={{ paddingRight: '2.5rem' }}
                >
                    <button
                        className={styles.toggleBtn}
                        type="button"
                        onClick={toggleShowPassword}
                        tabIndex={-1}
                    >
                        {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                </Input>

                {errorMsg && (
                    <div className={styles.errorMsg}>
                        {errorMsg}
                    </div>
                )}

                <div className={styles.forgotLink}>
                    <Link to={PATHS.FORGOT_PASSWORD}>Quên mật khẩu</Link>
                </div>

                <Button type="submit" loading={loading}>
                    Đăng Nhập
                </Button>
            </form>
        </section>
    );
};

export default LoginPage;