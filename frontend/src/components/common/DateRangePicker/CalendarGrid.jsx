import styles from './DateRangePicker.module.css';
import { generateMonthDays, WEEK_DAYS, MONTH_NAMES } from '@/hooks/useDateRangePicker';

/**
 * CalendarGrid – hiển thị lưới ngày của 1 tháng đơn.
 * Không chứa bất kỳ state nào — thuần UI.
 */
export default function CalendarGrid({ year, month, tempStart, tempEnd, isSameDay, isInRange, onDayClick }) {
    const days = generateMonthDays(year, month);

    return (
        <div className={styles.singleCalendar}>
            {/* Hàng tên thứ */}
            <div className={styles.weekGrid}>
                {WEEK_DAYS.map((d) => (
                    <span key={d} className={styles.weekDay}>{d}</span>
                ))}
            </div>

            {/* Lưới ngày */}
            <div className={styles.daysGrid}>
                {days.map((item, idx) => {
                    const isStart = isSameDay(item.date, tempStart);
                    const isEnd   = isSameDay(item.date, tempEnd);
                    const inRange = isInRange(item.date);

                    const cls = [
                        styles.dayBtn,
                        !item.isCurrentMonth          && styles.otherMonth,
                        isStart                        && styles.startDate,
                        isEnd                          && styles.endDate,
                        inRange && !isStart && !isEnd  && styles.inRange,
                    ].filter(Boolean).join(' ');

                    return (
                        <button
                            key={idx}
                            type="button"
                            disabled={!item.isCurrentMonth}
                            className={cls}
                            onClick={() => onDayClick(item.date)}
                        >
                            {item.date.getDate()}
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
