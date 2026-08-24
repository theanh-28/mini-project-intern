import { useState, useEffect, useCallback } from 'react';
import { auditLogService } from '@/services/auditLogService';

export function useAuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Phân trang theo con trỏ (Cursor-based Pagination)
  const [limit, setLimit] = useState(20);
  const [cursorHistory, setCursorHistory] = useState(['']); // Danh sách cursor các trang trước đó
  const [currentPageIndex, setCurrentPageIndex] = useState(0);
  const [nextCursor, setNextCursor] = useState(null);
  const [hasMore, setHasMore] = useState(false);

  // Bộ lọc
  const [filters, setFilters] = useState({
    search: '',
    action: '',
    table_name: '',
    startDate: '',
    endDate: '',
  });

  const [draftFilters, setDraftFilters] = useState({
    search: '',
    action: '',
    table_name: '',
    startDate: '',
    endDate: '',
  });

  // Chi tiết bản ghi Modal
  const [selectedLog, setSelectedLog] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState(null);

  // Hàm tải dữ liệu
  const fetchAuditLogs = useCallback(
    async (cursor = '', pageIdx = 0) => {
      setLoading(true);
      setError(null);
      try {
        const params = {
          limit,
          cursor: cursor || undefined,
          action: filters.action || undefined,
          table_name: filters.table_name || undefined,
          search: filters.search.trim() || undefined,
          created_at_from: filters.startDate ? `${filters.startDate}T00:00:00` : undefined,
          created_at_to: filters.endDate ? `${filters.endDate}T23:59:59` : undefined,
        };

        const data = await auditLogService.getAuditLogs(params);
        setLogs(data.audit_logs || []);
        setNextCursor(data.next_cursor || null);
        setHasMore(Boolean(data.has_more));
        setCurrentPageIndex(pageIdx);
      } catch (err) {
        console.error('Error fetching audit logs:', err);
        setError(err.response?.data?.detail || err.message || 'Không thể tải nhật ký kiểm toán');
      } finally {
        setLoading(false);
      }
    },
    [limit, filters]
  );

  // Tải lại khi filters hoặc limit thay đổi
  useEffect(() => {
    setCursorHistory(['']);
    fetchAuditLogs('', 0);
  }, [fetchAuditLogs]);

  // Chuyển sang trang tiếp theo
  const handleNextPage = () => {
    if (!hasMore || !nextCursor) return;
    const newHistory = [...cursorHistory, nextCursor];
    setCursorHistory(newHistory);
    fetchAuditLogs(nextCursor, currentPageIndex + 1);
  };

  // Quay lại trang trước
  const handlePrevPage = () => {
    if (currentPageIndex <= 0) return;
    const prevPageIndex = currentPageIndex - 1;
    const prevCursor = cursorHistory[prevPageIndex] || '';
    fetchAuditLogs(prevCursor, prevPageIndex);
  };

  // Quay về trang đầu tiên
  const handleFirstPage = () => {
    if (currentPageIndex <= 0) return;
    setCursorHistory(['']);
    fetchAuditLogs('', 0);
  };

  // Thay đổi draft filter
  const handleDraftChange = (field, value) => {
    setDraftFilters((prev) => ({ ...prev, [field]: value }));
  };

  const handleDateRangeChange = ({ startDate, endDate }) => {
    setDraftFilters((prev) => ({
      ...prev,
      startDate: startDate || '',
      endDate: endDate || '',
    }));
  };

  // Áp dụng bộ lọc
  const applyFilters = () => {
    setFilters({ ...draftFilters });
  };

  // Xóa bộ lọc
  const clearFilters = () => {
    const empty = {
      search: '',
      action: '',
      table_name: '',
      startDate: '',
      endDate: '',
    };
    setDraftFilters(empty);
    setFilters(empty);
  };

  const isFiltered = Boolean(
    filters.search ||
    filters.action ||
    filters.table_name ||
    filters.startDate ||
    filters.endDate
  );

  // Mở modal xem chi tiết bản ghi đầy đủ
  const openDetailModal = async (logItem) => {
    setSelectedLog(logItem);
    setDetailLoading(true);
    setDetailError(null);
    try {
      const fullDetail = await auditLogService.getAuditLogDetail(logItem.id);
      setSelectedLog(fullDetail);
    } catch (err) {
      console.error('Error fetching log detail:', err);
      setDetailError(err.response?.data?.detail || 'Không thể tải chi tiết bản ghi');
    } finally {
      setDetailLoading(false);
    }
  };

  const closeDetailModal = () => {
    setSelectedLog(null);
    setDetailError(null);
  };

  return {
    logs,
    loading,
    error,
    limit,
    setLimit,
    currentPageIndex,
    hasPrev: currentPageIndex > 0,
    hasNext: hasMore,
    handleFirstPage,
    handleNextPage,
    handlePrevPage,
    filters,
    draftFilters,
    handleDraftChange,
    handleDateRangeChange,
    applyFilters,
    clearFilters,
    isFiltered,
    selectedLog,
    detailLoading,
    detailError,
    openDetailModal,
    closeDetailModal,
    refetch: () => fetchAuditLogs(cursorHistory[currentPageIndex] || '', currentPageIndex),
  };
}
