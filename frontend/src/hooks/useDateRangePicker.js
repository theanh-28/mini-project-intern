import { useState, useRef, useEffect, useCallback } from 'react';

export const PRESETS = [
    { id: 'any', label: 'Any time' },
    { id: 'last7', label: 'Last 7 days' },
    { id: 'last30', label: 'Last 30 days' },
    { id: 'thisMonth', label: 'This Month' },
    { id: 'lastMonth', label: 'Last Month' },
    { id: 'custom', label: 'Custom range' },
];

export const WEEK_DAYS = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];

export const MONTH_NAMES = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
];


/** Trả về "YYYY-MM-DD" hoặc '' */
export const formatDateYMD = (d) => {
    if (!d || isNaN(d.getTime())) return '';
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
};

/** Trả về "DD/MM/YYYY" hoặc '' */
export const formatDateDMY = (d) => {
    if (!d || isNaN(d.getTime())) return '';
    const day = String(d.getDate()).padStart(2, '0');
    const m = String(d.getMonth() + 1).padStart(2, '0');
    return `${day}/${m}/${d.getFullYear()}`;
};

/** So sánh 2 Date theo ngày (bỏ giờ) */
export const isSameDay = (d1, d2) =>
    d1 && d2 &&
    d1.getFullYear() === d2.getFullYear() &&
    d1.getMonth() === d2.getMonth() &&
    d1.getDate() === d2.getDate();

/** Tạo mảng 42 ô lịch cho 1 tháng */
export const generateMonthDays = (year, month) => {
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const prevDays = new Date(year, month, 0).getDate();
    const days = [];

    for (let i = firstDay - 1; i >= 0; i--)
        days.push({ date: new Date(year, month - 1, prevDays - i), isCurrentMonth: false });

    for (let i = 1; i <= daysInMonth; i++)
        days.push({ date: new Date(year, month, i), isCurrentMonth: true });

    for (let i = 1; i <= 42 - days.length; i++)
        days.push({ date: new Date(year, month + 1, i), isCurrentMonth: false });

    return days;
};

/** Tính start/end từ preset id */
const calcPresetRange = (presetId) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const offset = (n) => { const d = new Date(today); d.setDate(today.getDate() + n); return d; };

    switch (presetId) {
        case 'last7': return { start: offset(-6), end: today };
        case 'last30': return { start: offset(-29), end: today };
        case 'thisMonth': return {
            start: new Date(today.getFullYear(), today.getMonth(), 1),
            end: new Date(today.getFullYear(), today.getMonth() + 1, 0),
        };
        case 'lastMonth': return {
            start: new Date(today.getFullYear(), today.getMonth() - 1, 1),
            end: new Date(today.getFullYear(), today.getMonth(), 0),
        };
        default: return { start: null, end: null };
    }
};

// Custom Hook
export const useDateRangePicker = ({ startDate, endDate, onChange }) => {
    const triggerRef = useRef(null);   // gắn vào trigger button
    const popoverRef = useRef(null);   // gắn vào popover div
    const [isOpen, setIsOpen] = useState(false);
    const [popoverPos, setPopoverPos] = useState({ top: 0, left: 0 });
    const [viewDate, setViewDate] = useState(() => {
        const d = new Date();
        // Trái = tháng trước, phải = tháng hiện tại
        return new Date(d.getFullYear(), d.getMonth() - 1, 1);
    });
    const [appliedPreset, setAppliedPreset] = useState('any');
    const [tempPreset, setTempPreset] = useState('any');
    const [tempStart, setTempStart] = useState(startDate ? new Date(startDate) : null);
    const [tempEnd, setTempEnd] = useState(endDate ? new Date(endDate) : null);

    // Đồng bộ khi props thay đổi (Clear filters từ bên ngoài)
    useEffect(() => {
        setTempStart(startDate ? new Date(startDate) : null);
        setTempEnd(endDate ? new Date(endDate) : null);
        if (!startDate && !endDate) {
            setAppliedPreset('any');
            setTempPreset('any');
        }
    }, [startDate, endDate]);

    // Click-outside: đăng ký 1 lần, dùng ref để đọc isOpen tránh stale closure
    const isOpenRef = useRef(isOpen);
    isOpenRef.current = isOpen;

    // Tháng ban đầu: ô trái = tháng trước, ô phải = tháng hiện tại
    const getInitialViewDate = useCallback(() => {
        if (startDate) {
            const d = new Date(startDate);
            // Hiển thị startDate ở ô phải → viewDate = tháng trước đó
            return new Date(d.getFullYear(), d.getMonth() - 1, 1);
        }
        const now = new Date();
        return new Date(now.getFullYear(), now.getMonth() - 1, 1);
    }, [startDate]);

    const handleCancel = useCallback(() => {
        setTempStart(startDate ? new Date(startDate) : null);
        setTempEnd(endDate ? new Date(endDate) : null);
        setTempPreset(appliedPreset);         // Reset tempPreset về preset đã Apply trước đó
        setViewDate(getInitialViewDate());   // reset lịch về tháng ban đầu
        setIsOpen(false);
    }, [startDate, endDate, appliedPreset, getInitialViewDate]);

    const handleCancelRef = useRef(handleCancel);
    handleCancelRef.current = handleCancel;

    useEffect(() => {
        const onMouseDown = (e) => {
            if (!isOpenRef.current) return;
            // Bỏ qua nếu click vào trigger button
            if (triggerRef.current && triggerRef.current.contains(e.target)) return;
            // Bỏ qua nếu click vào popover
            if (popoverRef.current && popoverRef.current.contains(e.target)) return;
            handleCancelRef.current();
        };
        document.addEventListener('mousedown', onMouseDown);
        return () => document.removeEventListener('mousedown', onMouseDown);
    }, []); // đăng ký 1 lần duy nhất khi mount

    // ── Derived values ────────────────────────────────────────────────────────

    const leftYear = viewDate.getFullYear();
    const leftMonth = viewDate.getMonth();
    const rightDate = new Date(leftYear, leftMonth + 1, 1);

    const buttonLabel = (() => {
        if (!startDate && !endDate) return 'Created: Any time';
        if (startDate && endDate)
            return `Created: ${formatDateDMY(new Date(startDate))} – ${formatDateDMY(new Date(endDate))}`;
        if (startDate) return `Created: From ${formatDateDMY(new Date(startDate))}`;
        return `Created: Until ${formatDateDMY(new Date(endDate))}`;
    })();

    const isInRange = (d) => tempStart && tempEnd && d >= tempStart && d <= tempEnd;

    // ── Handlers ─────────────────────────────────────────────────────────────

    const toggleOpen = () => {
        if (!isOpenRef.current && triggerRef.current) {
            // Tính vị trí fixed dựa theo trigger button
            const rect = triggerRef.current.getBoundingClientRect();
            setPopoverPos({ top: rect.bottom + 8, left: rect.left });
            // Reset lịch và preset tạm về trạng thái đã lưu mỗi lần mở lại
            setViewDate(getInitialViewDate());
            setTempStart(startDate ? new Date(startDate) : null);
            setTempEnd(endDate ? new Date(endDate) : null);
            setTempPreset(appliedPreset);
        }
        setIsOpen((v) => !v);
    };

    const applyPreset = (presetId) => {
        setTempPreset(presetId);
        const { start, end } = calcPresetRange(presetId);
        setTempStart(start);
        setTempEnd(end);
        if (start) setViewDate(new Date(start.getFullYear(), start.getMonth(), 1));
    };

    const handleDayClick = (date) => {
        setTempPreset('custom');
        if (!tempStart || tempEnd) {
            setTempStart(date);
            setTempEnd(null);
        } else {
            if (date < tempStart) { setTempStart(date); setTempEnd(null); }
            else setTempEnd(date);
        }
    };

    const handleApply = () => {
        setAppliedPreset(tempPreset); // ← Lưu lại preset chính thức được Apply
        onChange(formatDateYMD(tempStart), formatDateYMD(tempEnd));
        setIsOpen(false);
    };

    const prevMonth = () => setViewDate(new Date(leftYear, leftMonth - 1, 1));
    const nextMonth = () => setViewDate(new Date(leftYear, leftMonth + 1, 1));

    return {
        // refs
        triggerRef, popoverRef,
        // state
        isOpen, toggleOpen,
        // popover position (fixed)
        popoverStyle: {
            position: 'fixed',
            top: popoverPos.top,
            left: popoverPos.left,
            zIndex: 9999,
        },
        tempPreset, tempStart, tempEnd,
        // calendar
        leftYear, leftMonth,
        rightYear: rightDate.getFullYear(), rightMonth: rightDate.getMonth(),
        // labels & utils
        buttonLabel, isInRange, isSameDay, formatDateDMY,
        // handlers
        applyPreset, handleDayClick, handleApply, handleCancel, prevMonth, nextMonth,
    };
};
