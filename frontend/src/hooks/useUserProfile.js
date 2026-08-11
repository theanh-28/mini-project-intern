import { useState, useEffect, useCallback } from 'react'

import { adminService } from "@/services/adminService";

export const  useUserProfile = (userId) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [user, setUser] = useState({});

    const fetchUser = useCallback(async () => {
        if (!userId) return;
        
        setLoading(true);
        setError('');
        
        try {
            const data = await adminService.getUserById(userId);
            setUser(data.user || data || {});
        } catch (err) {
            const errData = err.response?.data?.error || err.response?.data?.detail || err.message;
            const errMsg = typeof errData === 'object' 
                ? (Array.isArray(errData) ? errData[0]?.msg : errData.msg || errData.message || JSON.stringify(errData)) 
                : errData;
            setError(errMsg || 'Lấy thông tin thất bại');
        } finally {
            setLoading(false);
        }
    }, [userId]);

    useEffect(() => {
        fetchUser();
    }, [fetchUser]);

    return {
        user,
        setUser,
        loading,
        error,
        fetchUser,
    };
}