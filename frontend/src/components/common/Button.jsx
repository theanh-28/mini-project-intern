import clsx from 'clsx';
import Spinner from './Spinner';
import styles from './Button.module.css';

export default function Button({
  children,
  type = 'button',
  loading = false,
  disabled = false,
  className = '',
  onClick,
  ...props
}) {
  return (
    <button
      type={type}
      className={clsx(styles.btn, className)}
      disabled={disabled || loading}
      onClick={onClick}
      {...props}
    >
      {loading ? <Spinner size={20} /> : children}
    </button>
  );
}
