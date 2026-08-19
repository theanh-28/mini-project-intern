import Input from '@/components/common/Input';
import Button from '@/components/common/Button';
import styles from './UserCreateModal.module.css';
import { Eye, EyeOff, LockKeyhole, User, Mail } from 'lucide-react';

export default function UserCreateModal({
    isOpen,
    closeModal,
    onSubmit,
    values,
    handleChange,
    errorMsg,
    msgSuccess,
    isSubmitting,
    showPassword,
    toggleShowPassword,
    showConfirmPassword,
    toggleShowConfirmPassword,
    resetForm,
}) {
    if (!isOpen) return null;

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
                        onChange={handleChange}
                        leftIcon={<User strokeWidth='3' size={18} style={{pointerEvents:'none'}}/>}
                    />
                    <Input 
                        containerClassName={styles.inputContainer} 
                        label="Email" 
                        type="email"
                        name='email'
                        placeholder="Enter email" 
                        value={values.email} 
                        onChange={handleChange} 
                        leftIcon={<Mail strokeWidth='3' size={18} style={{pointerEvents:'none'}}/>}
                    />
                    <Input 
                        containerClassName={styles.inputContainer} 
                        label="Password" 
                        name='password'
                        placeholder="Enter password" 
                        type={showPassword ? 'text' : 'password'} 
                        value={values.password} 
                        onChange={handleChange} 
                        leftIcon={<LockKeyhole strokeWidth='3' size={18} />}
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
                        containerClassName={styles.inputContainer} 
                        label="Confirm Password" 
                        placeholder="Confirm password" 
                        type={showConfirmPassword ? 'text' : 'password'} 
                        name='confirmPassword'
                        value={values.confirmPassword} 
                        onChange={handleChange}
                        leftIcon={<LockKeyhole strokeWidth='3' size={18} />} 
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
                        <Button className={`${styles.btn} ${styles.cancelBtn}`} type='button' onClick={closeModal}>
                            Cancel
                        </Button>
                        <Button className={`${styles.btn} ${styles.resetBtn}`} type='button' onClick={resetForm}>
                            Reset Form
                        </Button>
                        <Button className={`${styles.btn} ${styles.createBtn}`} type='submit' isLoading={isSubmitting}>
                            Create
                        </Button>
                    </div>
                </form>
            </section>
        </div>
    );
}