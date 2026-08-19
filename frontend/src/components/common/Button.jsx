import clsx from 'clsx';
import Spinner from './Spinner';
import styles from './Button.module.css';

export default function Button({
  children,
  type = 'button',
  isLoading = false,
  disabled = false,
  className = '',
  onClick,
  ...props
}) {
  return (
    <button
      type={type}
      className={clsx(styles.btn, className)}
      disabled={disabled || isLoading}
      onClick={onClick}
      {...props}
    >
      {isLoading ? <Spinner size={20} /> : children}
    </button>
  );
}
