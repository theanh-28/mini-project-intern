import { History, RotateCw } from 'lucide-react';
import styles from './AuditLogsPage.module.css';

import AuditLogFilter from '@/components/iam/audit_logs/AuditLogFilter';
import AuditLogTable from '@/components/iam/audit_logs/AuditLogTable';
import AuditLogDetailModal from '@/components/iam/audit_logs/AuditLogDetailModal';
import CursorPagination from '@/components/iam/audit_logs/CursorPagination';
import Button from '@/components/common/Button';

import { useAuditLogs } from '@/hooks/useAuditLogs';

export default function AuditLogsPage() {
  const {
    logs,
    loading,
    error,
    limit,
    currentPageIndex,
    hasPrev,
    hasNext,
    handleFirstPage,
    handleNextPage,
    handlePrevPage,
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
    refetch,
  } = useAuditLogs();

  return (
    <section className={styles.card}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <History size='24' strokeWidth='3' />
          <span className={styles.title}>Audit Logs</span>
        </div>

        <div className={styles.headerRight}>
          <Button
            className={styles.refreshBtn}
            onClick={refetch}
            disabled={loading}
            title="Refresh logs"
          >
            <RotateCw size={15} className={loading ? styles.spinning : ''} />
            <span>Refresh</span>
          </Button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className={styles.content}>
        {/* Filters Bar */}
        <div className={styles.filter}>
          <AuditLogFilter
            draftFilters={draftFilters}
            onDraftChange={handleDraftChange}
            onDateRangeChange={handleDateRangeChange}
            onApply={applyFilters}
            onClear={clearFilters}
            isFiltered={isFiltered}
          />
        </div>

        {/* Audit Log Table */}
        <div className={styles.table}>
          <AuditLogTable
            logs={logs}
            loading={loading}
            error={error}
            startIndex={currentPageIndex * limit}
            onViewDetail={openDetailModal}
          />
        </div>

        {/* Cursor-based Pagination Footer */}
        <div className={styles.footer}>
          <CursorPagination
            currentPageIndex={currentPageIndex}
            hasPrev={hasPrev}
            hasNext={hasNext}
            loading={loading}
            onFirst={handleFirstPage}
            onPrev={handlePrevPage}
            onNext={handleNextPage}
          />
        </div>
      </div>

      {/* Record Detail Modal */}
      {selectedLog && (
        <AuditLogDetailModal
          log={selectedLog}
          loading={detailLoading}
          error={detailError}
          onClose={closeDetailModal}
        />
      )}
    </section>
  );
}
