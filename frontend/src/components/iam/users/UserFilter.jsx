import { Search, RotateCcw, ChevronDown, ChevronUp, Filter } from 'lucide-react';
import styles from './UserFilter.module.css';
import Button from '@/components/common/Button';
import Input from '@/components/common/Input';
import DateRangePicker from '@/components/common/DateRangePicker/DateRangePicker';
import { useUserFilters } from '@/hooks/useUserFilters';

export default function UserFilter({ filters, onFilterChange }) {
    const {
        draftFilters,
        openSelect,
        handleSelectClick,
        handleSelectBlur,
        handleDraftChange,
        handleDateRangeChange,
        handleSearchKeyDown,
        applyFilters,
        clearFilters,
        isFiltered,
        isDraftActive,
    } = useUserFilters({ filters, onFilterChange });

    return (
        <div className={styles.filterBarScroll}>
            <div className={styles.filterBar}>
                {/* Ô Search Name hoặc Email */}
                <Input
                    type="text"
                    placeholder="Search name or email"
                    value={draftFilters.search}
                    onChange={(e) => handleDraftChange('search', e.target.value)}
                    onKeyDown={handleSearchKeyDown}
                    leftIcon={<Search size={16} />}
                    containerClassName={styles.searchBox}
                    className={styles.searchInput}
                />

                {/* Ô Lọc Status */}
                <div className={styles.selectWrapper}>
                    <select
                        className={`${styles.selectInput} ${draftFilters.status || openSelect === 'status' ? styles.active : ''}`}
                        value={draftFilters.status}
                        onClick={(e) => handleSelectClick('status', e)}
                        onChange={(e) => {
                            handleDraftChange('status', e.target.value);
                            handleSelectBlur();
                        }}
                        onBlur={handleSelectBlur}
                    >
                        <option value="">All Status</option>
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                    </select>
                    {openSelect === 'status' ? (
                        <ChevronUp size={15} className={styles.selectIcon} />
                    ) : (
                        <ChevronDown size={15} className={styles.selectIcon} />
                    )}
                </div>

                {/* Ô Lọc Role (Giữ lại phục vụ mô hình RBAC) */}
                <div className={styles.selectWrapper}>
                    <select
                        className={`${styles.selectInput} ${draftFilters.role || openSelect === 'role' ? styles.active : ''}`}
                        value={draftFilters.role}
                        onClick={(e) => handleSelectClick('role', e)}
                        onChange={(e) => {
                            handleDraftChange('role', e.target.value);
                            handleSelectBlur();
                        }}
                        onBlur={handleSelectBlur}
                    >
                        <option value="">All Roles</option>
                        <option value="admin">Admin</option>
                        <option value="user">User</option>
                    </select>
                    {openSelect === 'role' ? (
                        <ChevronUp size={15} className={styles.selectIcon} />
                    ) : (
                        <ChevronDown size={15} className={styles.selectIcon} />
                    )}
                </div>

                {/* Popover Date Range Picker */}
                <DateRangePicker
                    startDate={draftFilters.startDate}
                    endDate={draftFilters.endDate}
                    onChange={handleDateRangeChange}
                />

                {/* Nút Submit Lọc */}
                <Button
                    type="button"
                    className={styles.filterBtn}
                    onClick={applyFilters}
                    title="Apply Filters"
                >
                    <Filter size={14} /> Filter
                </Button>

                {/* Nút Clear Filters */}
                <Button
                    type="button"
                    className={styles.clearBtn}
                    onClick={clearFilters}
                    disabled={!isFiltered && !isDraftActive}
                    title="Clear All Filters"
                >
                    <RotateCcw size={14} /> Clear filters
                </Button>
            </div>
        </div>
    );
}
