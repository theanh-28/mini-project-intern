import styles from './UserUpdateModal.module.css';
import Input from '@/components/common/Input';
import Button from '@/components/common/Button';
import { User, Mail } from 'lucide-react';

export default function UserUpdateModal({
    isOpen,
    closeModal,
    onSubmit,
    values,
    handleChange,
    errorMsg,
    msgSuccess,
    isSubmitting,
}) {
    if (!isOpen) return null;

    return (
        <div className={styles.modalOverlay}>
            <section className={styles.card}>
                <header className={styles.title}>
                    User update form
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
                        leftIcon={<User strokeWidth='3' size={18} style={{ pointerEvents: 'none' }} />}
                    />

                    <Input 
                        containerClassName={styles.inputContainer} 
                        label="Email" 
                        type="email"
                        name='email'
                        placeholder="Enter email" 
                        value={values.email} 
                        onChange={handleChange} 
                        leftIcon={<Mail strokeWidth='3' size={18} style={{ pointerEvents: 'none' }} />}
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
                        <Button className={`${styles.btn} ${styles.updateBtn}`} type='submit' isLoading={isSubmitting}>
                            Update
                        </Button>
                    </div>
                </form>
            </section>
        </div>
    );
}