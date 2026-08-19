import { useState, useEffect } from 'react';

export const usePagination = ({ currentPage, totalPages, onPageChange }) => {
    const [inputValue, setInputValue] = useState(currentPage);

    // Đồng bộ inputValue khi currentPage thay đổi từ bên ngoài (click nút Next/Prev)
    useEffect(() => {
        setInputValue(currentPage);
    }, [currentPage]);

    // Hàm xử lý áp dụng trang mới khi người dùng bấm Enter hoặc Blur
    const commitPageChange = (targetValue) => {
        let num = parseInt(targetValue, 10);
        
        if (isNaN(num) || num < 1) {
            num = 1;
        } else if (num > totalPages) {
            num = totalPages;
        }

        setInputValue(num);

        // Chỉ gửi request API nếu số trang thực sự THAY ĐỔI so với currentPage hiện tại
        if (num !== currentPage) {
            onPageChange(num);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            e.target.blur(); // Trình duyệt sẽ tự động kích hoạt sự kiện onBlur
        }
    };

    const handleInputChange = (e) => {
        setInputValue(e.target.value);
    };

    const handleBlur = () => {
        commitPageChange(inputValue);
    };

    const handleButtonClick = (newPage) => {
        if (newPage >= 1 && newPage <= totalPages && newPage !== currentPage) {
            onPageChange(newPage);
        }
    };

    return {
        inputValue,
        handleInputChange,
        handleKeyDown,
        handleBlur,
        handleButtonClick,
    };
};
