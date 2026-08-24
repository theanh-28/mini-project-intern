import { useState } from 'react';
import { Search, RotateCcw, ChevronDown, ChevronUp, Filter } from 'lucide-react';
import styles from './AuditLogFilter.module.css';
import Button from '@/components/common/Button';
import Input from '@/components/common/Input';
import DateRangePicker from '@/components/common/DateRangePicker/DateRangePicker';

const ACTION_OPTIONS = [
  { value: '', label: 'All Actions' },
  { value: 'CREATE', label: 'CREATE' },
  { value: 'UPDATE', label: 'UPDATE' },
  { value: 'DELETE', label: 'DELETE' },
];

const TABLE_OPTIONS = [
  { value: '', label: 'All Entities' },
  { value: 'users', label: 'Users' },
  { value: 'roles', label: 'Roles' },
  { value: 'permissions', label: 'Permissions' },
  { value: 'user_roles', label: 'User Roles' },
];

export default function AuditLogFilter({
  draftFilters,
  onDraftChange,
  onDateRangeChange,
  onApply,
  onClear,
  isFiltered,
}) {
  const [openSelect, setOpenSelect] = useState(null);

  const isDraftActive = Boolean(
    draftFilters?.search ||
    draftFilters?.action ||
    draftFilters?.tableName ||
    draftFilters?.startDate ||
    draftFilters?.endDate
  );

  const handleSelectClick = (name, e) => {
    e.stopPropagation();
    setOpenSelect((prev) => (prev === name ? null : name));
  };

  const handleSelectBlur = () => {
    setOpenSelect(null);
  };

  const handleSearchKeyDown = (e) => {
    if (e.key === 'Enter') {
      onApply();
    }
  };

  return (
    <div className={styles.filterBarScroll}>
      <div className={styles.filterBar}>
        {/* Search input */}
        <Input
          type="text"
          placeholder="Search actor, table, or IP"
          value={draftFilters.search}
          onChange={(e) => onDraftChange('search', e.target.value)}
          onKeyDown={handleSearchKeyDown}
          leftIcon={<Search size={16} />}
          containerClassName={styles.searchBox}
          className={styles.searchInput}
        />

        {/* Action Select */}
        <div className={styles.selectWrapper}>
          <select
            className={`${styles.selectInput} ${draftFilters.action || openSelect === 'action' ? styles.active : ''}`}
            value={draftFilters.action}
            onClick={(e) => handleSelectClick('action', e)}
            onChange={(e) => {
              onDraftChange('action', e.target.value);
              handleSelectBlur();
            }}
            onBlur={handleSelectBlur}
          >
            {ACTION_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          {openSelect === 'action' ? (
            <ChevronUp size={15} className={styles.selectIcon} />
          ) : (
            <ChevronDown size={15} className={styles.selectIcon} />
          )}
        </div>

        {/* Table / Entity Select */}
        <div className={styles.selectWrapper}>
          <select
            className={`${styles.selectInput} ${draftFilters.table_name || openSelect === 'table_name' ? styles.active : ''}`}
            value={draftFilters.table_name}
            onClick={(e) => handleSelectClick('table_name', e)}
            onChange={(e) => {
              onDraftChange('table_name', e.target.value);
              handleSelectBlur();
            }}
            onBlur={handleSelectBlur}
          >
            {TABLE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          {openSelect === 'table_name' ? (
            <ChevronUp size={15} className={styles.selectIcon} />
          ) : (
            <ChevronDown size={15} className={styles.selectIcon} />
          )}
        </div>

        {/* Date Range Picker */}
        <DateRangePicker
          startDate={draftFilters.startDate}
          endDate={draftFilters.endDate}
          onChange={onDateRangeChange}
        />

        {/* Filter Button */}
        <Button
          type="button"
          className={styles.filterBtn}
          onClick={onApply}
          title="Apply Filters"
        >
          <Filter size={14} /> Filter
        </Button>

        {/* Nút Clear Filters */}
        <Button
          type="button"
          className={styles.clearBtn}
          onClick={onClear}
          disabled={!isFiltered && !isDraftActive}
          title="Clear All Filters"
        >
          <RotateCcw size={14} /> Clear filters
        </Button>
      </div>
    </div>
  );
}
