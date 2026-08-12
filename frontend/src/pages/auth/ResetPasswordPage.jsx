import { Link } from 'react-router-dom';
import { ArrowLeft, Lock, Eye, EyeOff, Info } from 'lucide-react';

import { useResetPassword } from '@/hooks/useResetPassword';
import { PATHS } from '@/constants/routes';
import Input from '@/components/common/Input';
import Button from '@/components/common/Button';
import styles from './ResetPasswordPage.module.css';

export default function ResetPasswordPage() {
    const {
        values,
        errorMsg,
        msgSuccess,
        handleChange,
        showPassword,
        toggleShowPassword,
        showConfirmPassword,
        toggleShowConfirmPassword,
        onSubmit,
        isSubmitting,
    } = useResetPassword();

    return (
        <section className={styles.card}>
            <div className={styles.header}>
                <h2>Set New Password</h2>
            </div>

            <form onSubmit={onSubmit} className={styles.form} noValidate>
                <Input
                    label="New Password"
                    type={showPassword ? 'text' : 'password'}
                    id="password"
                    name="password"
                    placeholder="Enter new password"
                    value={values.password}
                    onChange={handleChange}
                    disabled={isSubmitting || Boolean(msgSuccess)}
                    leftIcon={<Lock size={18} strokeWidth={3} />}
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

                <Input
                    label="Confirm New Password"
                    type={showConfirmPassword ? 'text' : 'password'}
                    id="confirmPassword"
                    name="confirmPassword"
                    placeholder="Re-enter new password"
                    value={values.confirmPassword}
                    onChange={handleChange}
                    disabled={isSubmitting || Boolean(msgSuccess)}
                    leftIcon={<Lock size={18} strokeWidth={3} />}
                    required
                    rightIcon={
                        <button
                            type="button"
                            onClick={toggleShowConfirmPassword}
                            tabIndex={-1}
                        >
                            {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                        </button>
                    }
                />

                <div className={styles.infoTooltipContainer}>
                    <span className={styles.infoTrigger}>
                        <Info size={15} /> Password requirements
                    </span>
                    <div className={styles.tooltipBox}>
                        <p className={styles.tooltipTitle}>Password requirements:</p>
                        <ul>
                            <li>At least 8 characters long</li>
                            <li>Uppercase & lowercase letters (A-Z, a-z)</li>
                            <li>At least 1 number (0-9)</li>
                            <li>At least 1 special character (!@#$%^&*)</li>
                        </ul>
                    </div>
                </div>

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

                <Button type="submit" isLoading={isSubmitting} disabled={isSubmitting || Boolean(msgSuccess)}>
                    Reset Password
                </Button>

                <div className={styles.backLink}>
                    <Link to={PATHS.LOGIN}>
                        <ArrowLeft size={16} /> Back to Sign In
                    </Link>
                </div>
            </form>
        </section>
    );
}
