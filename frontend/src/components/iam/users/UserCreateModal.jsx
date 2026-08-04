
import Input from '@/components/common/Input';
import Button from '@/components/common/Button';
import styles from './UserCreateModal.module.css';
import { Eye, EyeOff } from 'lucide-react';

export default function UserCreateModal({ 
    open, 
    setShowModal, 
    onSubmit, 
    onChange, 
    errorMsg, 
    msgSuccess, 
    showPassword, 
    toggleShowPassword,
    showConfirmPassword,
    toggleShowConfirmPassword,
    values, 
    resetForm,
    isSubmitting
}) {
    if (!open) return null;

    return (
        <div className={styles.modalOverlay}>
            <section className={styles.card}>
                <header className={styles.title}>
                    User creation form
                </header>

                <form onSubmit={onSubmit} className={styles.form} noValidate>
                    <Input 
                        containerClassName={styles.inputContainer} 
                        type="text"
                        name='name'
                        value={values.name}
                        label="Username" 
                        placeholder="Enter username" 
                        onChange={onChange}
                    />
                    <Input 
                        containerClassName={styles.inputContainer} 
                        label="Email" 
                        type="email"
                        name='email'
                        placeholder="Enter email" 
                        value={values.email} 
                        onChange={onChange} 
                    />
                    <Input 
                        containerClassName={styles.inputContainer} 
                        label="Password" 
                        name='password'
                        placeholder="Enter password" 
                        type={showPassword ? 'text' : 'password'} 
                        value={values.password} 
                        onChange={onChange} 
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
                    <Input 
                        containerClassName={styles.inputContainer} 
                        label="Confirm Password" 
                        placeholder="Confirm password" 
                        type={showConfirmPassword ? 'text' : 'password'} 
                        name='confirmPassword'
                        value={values.confirmPassword} 
                        onChange={onChange} 
                    >
                        <button
                            className={styles.toggleBtn}
                            type="button"
                            onClick={toggleShowConfirmPassword}
                            tabIndex={-1}
                        >
                            {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                        </button>
                    </Input>

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

                    <div className={styles.btns}>
                        <Button className={`${styles.btn} ${styles.createBtn}`} type='submit' isLoading={isSubmitting}>
                            Create
                        </Button>
                        <Button className={`${styles.btn} ${styles.resetBtn}`} type='button' onClick={resetForm}>
                            Reset Form
                        </Button>
                        <Button className={`${styles.btn} ${styles.closeBtn}`} type='button' onClick={() => setShowModal(false)}>
                            Close
                        </Button>
                    </div>
                </form>
            </section>
        </div>
    );
}