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
  leftIcon,
  rightIcon,
  ...props
}) {
  return (
    <div className={clsx(styles.inputGroup, containerClassName)}>
      {label && <label htmlFor={id}>{label}</label>}
      <div className={styles.inputWrapper}>
        {leftIcon && <span className={styles.leftIcon}>{leftIcon}</span>}

        <input
          id={id}
          name={name}
          type={type}
          {...(type === 'checkbox' ? { checked: value } : { value })}
          onChange={onChange}
          placeholder={placeholder}
          disabled={disabled}
          required={required}
          className={clsx(
            styles.input,
            leftIcon && styles.hasLeftIcon,
            rightIcon && styles.hasRightIcon, 
            className
          )}
          {...props}
        />

        {rightIcon && <span className={styles.rightIcon}>{rightIcon}</span>}

        {children}
      </div>
    </div>
  );
}
