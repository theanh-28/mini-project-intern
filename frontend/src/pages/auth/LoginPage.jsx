import { Link } from 'react-router-dom';
import { EyeOff, Eye, Mail, Lock } from 'lucide-react';

import { useLogin } from '@/hooks/useLogin';
import { PATHS } from '@/constants/routes';
import Input from '@/components/common/Input';
import Button from '@/components/common/Button';
import styles from './LoginPage.module.css';

const LoginPage = () => {
    const {
        values,
        errorMsg,
        handleChange,
        showPassword,
        toggleShowPassword,
        onSubmit,
        isSubmitting,
    } = useLogin();

    return (
        <section className={styles.card}>
            <div className={styles.header}>
                <h2>Sign In</h2>
            </div>

            <form onSubmit={onSubmit} className={styles.form} noValidate>
                <Input
                    label="Email"
                    type="email"
                    id="email"
                    name="email"
                    placeholder="abc@example.com"
                    value={values.email}
                    onChange={handleChange}
                    disabled={isSubmitting}
                    leftIcon={<Mail size={18} strokeWidth={3}/>}
                    required
                />

                <Input
                    label="Password"
                    type={showPassword ? 'text' : 'password'}
                    id="password"
                    name="password"
                    placeholder="*********"
                    value={values.password}
                    onChange={handleChange}
                    disabled={isSubmitting}
                    leftIcon={<Lock size={18} strokeWidth={3}/>}
                    required
                    rightIcon={
                        <button
                            type="button"
                            onClick={toggleShowPassword}
                            tabIndex={-1}
                        >
                            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                        </button>
                    }
                />

                {errorMsg && (
                    <div className={styles.errorMsg}>
                        {errorMsg}
                    </div>
                )}

                <div className={styles.forgotLink}>
                    <Link to={PATHS.FORGOT_PASSWORD}>Forgot password?</Link>
                </div>

                <Button type="submit" isLoading={isSubmitting}>
                    Sign In
                </Button>
            </form>
        </section>
    );
};

export default LoginPage;