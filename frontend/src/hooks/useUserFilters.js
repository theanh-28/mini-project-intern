import { useState, useEffect } from 'react';

const EMPTY_FILTERS = {
    search: '',
    status: '',
    role: '',
    startDate: '',
    endDate: '',
};

export const useUserFilters = ({ filters, onFilterChange }) => {
    // Local draft state chứa các giá trị đang chọn trong form lọc trước khi bấm nút Filter
    const [draftFilters, setDraftFilters] = useState(filters || EMPTY_FILTERS);
    const [openSelect, setOpenSelect] = useState(null);

    // Đồng bộ draftFilters khi filters từ bên ngoài thay đổi
    useEffect(() => {
        setDraftFilters(filters || EMPTY_FILTERS);
    }, [filters]);

    const handleSelectClick = (field, e) => {
        if (openSelect === field) {
            setOpenSelect(null);
            e.target.blur();
        } else {
            setOpenSelect(field);
        }
    };

    const handleSelectBlur = () => {
        setOpenSelect(null);
    };

    const handleDraftChange = (field, value) => {
        setDraftFilters((prev) => ({ ...prev, [field]: value }));
    };

    const handleDateRangeChange = (startDate, endDate) => {
        setDraftFilters((prev) => ({ ...prev, startDate, endDate }));
    };

    // Hàm submit bộ lọc: Bắt buộc bấm nút Filter hoặc gõ Enter
    const applyFilters = () => {
        setOpenSelect(null);
        onFilterChange(draftFilters);
    };

    // Hàm xóa sạch bộ lọc
    const clearFilters = () => {
        setOpenSelect(null);
        setDraftFilters(EMPTY_FILTERS);
        onFilterChange(EMPTY_FILTERS);
    };

    const isFiltered = Object.values(filters).some(Boolean);
    const isDraftActive = Object.values(draftFilters).some(Boolean);

    return {
        draftFilters,
        openSelect,
        handleSelectClick,
        handleSelectBlur,
        handleDraftChange,
        handleDateRangeChange,
        handleSearchKeyDown: (e) => {
            if (e.key === 'Enter') {
                e.target.blur();
                applyFilters();
            }
        },
        applyFilters,
        clearFilters,
        isFiltered,
        isDraftActive,
    };
};

