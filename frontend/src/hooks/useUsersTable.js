import { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';

export const useUsersTable = () => {
    const [users, setUsers] = useState([]);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [total, setTotal] = useState(0);

    const [filters, setFilters] = useState({
        search: '',
        status: '',
        role: '',
        startDate: '',
        endDate: '',
    });

    const fetchUsers = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await adminService.getUsers({ page, per_page: 20, ...filters });
            setUsers(data.users || []);
            setTotalPages(data.total_pages || 1);
            setTotal(data.total || 0);
        } catch (err) {
            const errData = err.response?.data?.error || err.response?.data?.detail || err.message;
            const errMsg = typeof errData === 'object' 
                ? (Array.isArray(errData) ? errData[0]?.msg : errData.msg || errData.message || JSON.stringify(errData)) 
                : errData;
            setError(errMsg || 'Có lỗi xảy ra, vui lòng thử lại');
        } finally {
            setLoading(false);
        }
    }, [page, filters]);

    useEffect(() => {
        fetchUsers();
    }, [fetchUsers]);

    // Khi bộ lọc thay đổi, reset về trang 1 và lưu bộ lọc mới
    const handleFilterChange = (newFilters) => {
        setPage(1);
        setFilters(newFilters);
    };

    return {
        users,
        page,
        handlePageChange: setPage,
        totalPages,
        total,
        loading,
        error,
        fetchUsers,
        filters,
        handleFilterChange,
    };
};