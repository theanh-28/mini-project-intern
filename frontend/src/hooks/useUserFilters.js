import { useState, useEffect } from 'react';

const EMPTY_FILTERS = {
    search: '',
    status: '',
    role: '',
    startDate: '',
    endDate: '',
};

export const useUserFilters = ({ filters, onFilterChange }) => {
    const [searchBuffer, setSearchBuffer] = useState(filters?.search || '');
    const [openSelect, setOpenSelect]     = useState(null);

    // Đồng bộ searchBuffer khi Clear filters được bấm từ bên ngoài
    useEffect(() => {
        setSearchBuffer(filters?.search || '');
    }, [filters?.search]);

    const commitSearch = () => {
        const trimmed = searchBuffer.trim();
        if (trimmed !== filters.search) {
            onFilterChange({ ...filters, search: trimmed });
        }
    };

    const handleSelectClick = (field, e) => {
        if (openSelect === field) {
            setOpenSelect(null);
            e.target.blur();
        } else {
            setOpenSelect(field);
        }
    };

    const handleSelectChange = (field, value, e) => {
        onFilterChange({ ...filters, [field]: value });
        setOpenSelect(null);
        if (e?.target) e.target.blur();
    };

    const isFiltered = Object.values(filters).some(Boolean);

    return {
        searchBuffer,
        setSearchBuffer,
        openSelect,
        handleSelectClick,
        handleSelectBlur: () => setOpenSelect(null),
        // Bấm Enter trên ô Search → commit ngay
        handleSearchKeyDown: (e) => e.key === 'Enter' && e.target.blur(),
        handleSearchBlur: commitSearch,
        // Thay đổi select Status / Role / Date → cập nhật ngay
        handleSelectChange,
        handleDateRangeChange: (startDate, endDate) => onFilterChange({ ...filters, startDate, endDate }),
        clearFilters: () => {
            setSearchBuffer('');
            setOpenSelect(null);
            onFilterChange(EMPTY_FILTERS);
        },
        isFiltered,
    };
};

