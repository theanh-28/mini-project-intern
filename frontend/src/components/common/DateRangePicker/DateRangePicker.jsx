import { Calendar as CalendarIcon, ChevronLeft, ChevronRight, ChevronDown, ChevronUp } from 'lucide-react';
import styles from './DateRangePicker.module.css';
import CalendarGrid from './CalendarGrid';
import { useDateRangePicker, PRESETS, MONTH_NAMES } from '@/hooks/useDateRangePicker';

export default function DateRangePicker({ startDate, endDate, onChange }) {
    const {
        triggerRef, popoverRef, isOpen, toggleOpen, popoverStyle,
        tempPreset, tempStart, tempEnd,
        leftYear, leftMonth, rightYear, rightMonth,
        buttonLabel, isInRange, isSameDay, formatDateDMY,
        applyPreset, handleDayClick, handleApply, handleCancel, prevMonth, nextMonth,
    } = useDateRangePicker({ startDate, endDate, onChange });

    return (
        <div className={styles.container}>
            {/* ── Trigger Button ─────────────────────────────────────── */}
            <button
                ref={triggerRef}
                type="button"
                className={`${styles.triggerBtn} ${isOpen || startDate || endDate ? styles.active : ''}`}
                onClick={toggleOpen}
            >
                <CalendarIcon size={15} />
                <span>{buttonLabel}</span>
                {isOpen ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
            </button>

            {/* ── Popover ────────────────────────────────────────────── */}
            {isOpen && (
                <div className={styles.popover} ref={popoverRef} style={popoverStyle}>
                    <div className={styles.body}>

                        {/* Cột trái: Quick Presets */}
                        <div className={styles.presetColumn}>
                            {PRESETS.map((preset) => (
                                <button
                                    key={preset.id}
                                    type="button"
                                    className={`${styles.presetBtn} ${tempPreset === preset.id ? styles.activePreset : ''}`}
                                    onClick={() => applyPreset(preset.id)}
                                >
                                    {preset.label}
                                </button>
                            ))}
                        </div>

                        {/* Cột phải: Lịch kép */}
                        <div className={styles.calendarColumn}>
                            {/* Nav header */}
                            <div className={styles.navHeader}>
                                <button type="button" className={styles.navBtn} onClick={prevMonth}>
                                    <ChevronLeft size={16} />
                                </button>
                                <span className={styles.monthTitle}>{MONTH_NAMES[leftMonth]}  {leftYear}</span>
                                <span className={styles.monthTitle}>{MONTH_NAMES[rightMonth]} {rightYear}</span>
                                <button type="button" className={styles.navBtn} onClick={nextMonth}>
                                    <ChevronRight size={16} />
                                </button>
                            </div>

                            {/* 2 lịch song song */}
                            <div className={styles.calendarsWrapper}>
                                <CalendarGrid
                                    year={leftYear} month={leftMonth}
                                    tempStart={tempStart} tempEnd={tempEnd}
                                    isSameDay={isSameDay} isInRange={isInRange}
                                    onDayClick={handleDayClick}
                                />
                                <CalendarGrid
                                    year={rightYear} month={rightMonth}
                                    tempStart={tempStart} tempEnd={tempEnd}
                                    isSameDay={isSameDay} isInRange={isInRange}
                                    onDayClick={handleDayClick}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Footer */}
                    <div className={styles.footer}>
                        <div className={styles.selectedSummary}>
                            Selected: {tempStart ? formatDateDMY(tempStart) : 'Any'}
                            {tempEnd ? ` – ${formatDateDMY(tempEnd)}` : ''}
                        </div>
                        <div className={styles.footerBtns}>
                            <button type="button" className={styles.cancelBtn} onClick={handleCancel}>
                                Cancel
                            </button>
                            <button type="button" className={styles.applyBtn} onClick={handleApply}>
                                Apply
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
