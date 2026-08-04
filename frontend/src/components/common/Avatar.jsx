import  { useState } from 'react';
import styles from './Avatar.module.css';

export default function Avatar({ src, name, size = 'md', shape = 'circle', className = ''}) {
    const [isError, setIsError] = useState(false);

    // Lấy ký tự đầu của tên là chữ đại diện 
    const getInitials = (fullName) => {
        if (!fullName) return '?';
        const parts = fullName.trim().split(' ');
        if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
        return (parts[0].charAt(0) + parts[parts.length-1].charAt(0)).toUpperCase();
    }

    // Tạo class
    const avatarClass = `${styles.avatar} ${styles[size]} ${styles[shape]} ${styles[className]}`;

    // Nếu có ảnh và không lỗi
    if (src && !isError) {
        return (
            <img 
                src={src}
                alt={name || 'User Avatar'} 
                className={avatarClass} 
                onError={() => setIsError(true)}
            />
        );
    }

    // Nếu ảnh bị lỗi
    return (
        <div className={`${avatarClass} ${styles.placeholder}`}>
            {getInitials(name)}
        </div>
    )
}