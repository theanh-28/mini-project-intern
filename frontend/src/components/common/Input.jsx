import clsx from 'clsx';
import styles from './Input.module.css';

export default function Input({
  label,
  id,
  name,
  type = 'text',
  value,
  onChange,
  placeholder,
  disabled = false,
  required = false,
  children,
  className = '',
  containerClassName = '',
  ...props
}) {
  return (
    <div className={clsx(styles.inputGroup, containerClassName)}>
      {label && <label htmlFor={id}>{label}</label>}
      <div className={styles.inputWrapper}>
        <input
          id={id}
          name={name}
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
