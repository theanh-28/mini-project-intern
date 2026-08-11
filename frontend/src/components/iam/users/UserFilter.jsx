import { Search, RotateCcw, ChevronDown, ChevronUp } from 'lucide-react';
import styles from './UserFilter.module.css';
import Button from '@/components/common/Button';
import Input from '@/components/common/Input';
import DateRangePicker from '@/components/common/DateRangePicker/DateRangePicker';
import { useUserFilters } from '@/hooks/useUserFilters';

export default function UserFilter({ filters, onFilterChange }) {
    const {
        searchBuffer,
        setSearchBuffer,
        openSelect,
        handleSelectClick,
        handleSelectBlur,
        handleSearchKeyDown,
        handleSearchBlur,
        handleSelectChange,
        handleDateRangeChange,
        clearFilters,
        isFiltered,
    } = useUserFilters({ filters, onFilterChange });

    return (
        <div className={styles.filterBarScroll}>
            <div className={styles.filterBar}>
                {/* Ô Search Name hoặc Email */}
                <Input
                    type="text"
                    placeholder="Search name or email"
                    value={searchBuffer}
                    onChange={(e) => setSearchBuffer(e.target.value)}
                    onKeyDown={handleSearchKeyDown}
                    onBlur={handleSearchBlur}
                    leftIcon={<Search size={16} />}
                    containerClassName={styles.searchBox}
                    className={styles.searchInput}
                />

                {/* Ô Lọc Status */}
                <div className={styles.selectWrapper}>
                    <select
                        className={`${styles.selectInput} ${filters.status || openSelect === 'status' ? styles.active : ''}`}
                        value={filters.status}
                        onClick={(e) => handleSelectClick('status', e)}
                        onChange={(e) => handleSelectChange('status', e.target.value, e)}
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

                {/* Ô Lọc Role */}
                <div className={styles.selectWrapper}>
                    <select
                        className={`${styles.selectInput} ${filters.role || openSelect === 'role' ? styles.active : ''}`}
                        value={filters.role}
                        onClick={(e) => handleSelectClick('role', e)}
                        onChange={(e) => handleSelectChange('role', e.target.value, e)}
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
                    startDate={filters.startDate}
                    endDate={filters.endDate}
                    onChange={handleDateRangeChange}
                />

                {/* Nút Clear Filters luôn hiển thị ngang hàng */}
                <Button
                    type="button"
                    className={styles.clearBtn}
                    onClick={clearFilters}
                    disabled={!isFiltered}
                    title="Clear All Filters"
                >
                    <RotateCcw size={14} /> Clear filters
                </Button>
            </div>
        </div>
    );
}
