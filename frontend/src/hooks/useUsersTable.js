import { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';

export const useUsersTable = () => {
    const [users, setUsers] = useState([]);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [total, setTotal] = useState(0);

    const fetchUsers = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const currentPage = Number(page) || 1;
            const data = await adminService.getUsers({ page: currentPage, per_page: 20 });
            setUsers(data.users || []);
            setTotalPages(data.total_pages || 1);
            setTotal(data.total || 0);
        } catch (err) {
            setError(err);
        } finally {
            setLoading(false);
        }
    }, [page]);

    useEffect(() => {
        fetchUsers();
    }, [fetchUsers]);

    // Hàm xử lý nhập số trang
    const handlePageInputChange = (value) => {
        // Nếu xóa rỗng ô input thì cho phép tạm thời rỗng
        if (value === '') {
            setPage('');
            return;
        }
        let num = parseInt(value, 10);
        if (isNaN(num)) return;
        // Ép giá trị nằm trong khoảng: 1 <= num <= totalPages
        if (num < 1) num = 1;
        if (num > totalPages) num = totalPages;
        setPage(num);
    };
    // Khi người dùng click ra ngoài mà ô input đang rỗng -> trả về trang 1
    const handleBlur = () => {
        if (!page) {
            setPage(1);
        }
    };

    return {
        users,
        page,
        handlePageInputChange,
        handleBlur,
        totalPages,
        loading,
        error,
        total,
        fetchUsers,
    };
};