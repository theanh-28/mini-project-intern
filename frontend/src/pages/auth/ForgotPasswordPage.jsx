import { Link } from 'react-router-dom';
import { ArrowLeft, Mail } from 'lucide-react';

import { useForgotPassword } from '@/hooks/useForgotPassword';
import { PATHS } from '@/constants/routes';
import Input from '@/components/common/Input';
import Button from '@/components/common/Button';
import styles from './ForgotPasswordPage.module.css';

export default function ForgotPasswordPage() {
    const {
        values,
        errorMsg,
        msgSuccess,
        handleChange,
        onSubmit,
        isSubmitting,
        countdown,
        isCooldown,
    } = useForgotPassword();

    return (
        <section className={styles.card}>
            <div className={styles.header}>
                <h2>Forgot Password?</h2>
            </div>

            <form onSubmit={onSubmit} className={styles.form} noValidate>
                <Input
                    label="Email Address"
                    type="email"
                    id="email"
                    name="email"
                    placeholder="name@example.com"
                    value={values.email}
                    onChange={handleChange}
                    disabled={isSubmitting}
                    leftIcon={<Mail size={18} strokeWidth={3}/>}
                    required
                />

                {errorMsg && (
                    <div className={styles.errorMsg}>
                        {errorMsg}
                    </div>
                )}

                {msgSuccess && (
                    <div className={styles.successMsg}>
                        {msgSuccess}
                    </div>
                )}

                <Button type="submit" isLoading={isSubmitting} disabled={isSubmitting || isCooldown}>
                    {isCooldown ? `Resend link in ${countdown}s` : 'Send Reset Link'}
                </Button>

                <div className={styles.backLink}>
                    <Link to={PATHS.LOGIN}>
                        <ArrowLeft size={16} /> Back to Sign In
                    </Link>
                </div>
            </form>
        </section>
    );
};
