import styles from './Switch.module.css';

export default function Switch({
    checked,
    onChange,
    name,
}) {
    return (
        <label className={styles.switch}>
            <input
                name={name}
                type="checkbox"
                checked={!!checked}
                onChange={onChange}
            />
            <span className={styles.slider}> </span>
        </label>
    )
}