import clsx from 'clsx';
import styles from './Input.module.css';

export default function Input({
  label,
  id,
  type = 'text',
  value,
  onChange,
  placeholder,
  disabled = false,
  required = false,
  children,
  className = '',
  ...props
}) {
  return (
    <div className={styles.inputGroup}>
      {label && <label htmlFor={id}>{label}</label>}
      <div className={styles.inputWrapper}>
        <input
          id={id}
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          disabled={disabled}
          required={required}
          className={clsx(styles.input, className)}
          {...props}
        />
        {children}
      </div>
    </div>
  );
}
