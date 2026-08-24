import styles from './AuditLogTable.module.css';
import Spinner from '@/components/common/Spinner';
import Button from '@/components/common/Button';
import { Eye, ShieldAlert, PlusCircle, Edit, Trash2 } from 'lucide-react';

export default function AuditLogTable({
  logs,
  loading,
  error,
  startIndex = 0,
  onViewDetail,
}) {
  const renderActionBadge = (action) => {
    const act = (action || '').toUpperCase();
    switch (act) {
      case 'CREATE':
        return (
          <div className={styles.badgeCreate}>
            <PlusCircle size={13} strokeWidth={2.5} color="var(--color-success)" />
            <span>Create</span>
          </div>
        );
      case 'UPDATE':
        return (
          <div className={styles.badgeUpdate}>
            <Edit size={13} strokeWidth={2.5} color="var(--color-warning)" />
            <span>Update</span>
          </div>
        );
      case 'DELETE':
        return (
          <div className={styles.badgeDelete}>
            <Trash2 size={13} strokeWidth={2.5} color="var(--color-error)" />
            <span>Delete</span>
          </div>
        );
      default:
        return (
          <div className={styles.badgeDefault}>
            <span>{act || '-'}</span>
          </div>
        );
    }
  };

  const formatTimestamp = (isoString) => {
    if (!isoString) return '-';
    const date = new Date(isoString);
    return date.toLocaleString('vi-VN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <table className={styles.table}>
      <thead>
        <tr>
          <th style={{ width: '45px' }}>#</th>
          <th>Timestamp</th>
          <th>Actor</th>
          <th>Action</th>
          <th>Target Entity</th>
          <th>IP Address</th>
          <th style={{ textAlign: 'center' }}>Action</th>
        </tr>
      </thead>
      <tbody>
        {loading ? (
          <tr>
            <td colSpan="7">
              <div className={styles.loadingContainer}>
                <Spinner />
              </div>
            </td>
          </tr>
        ) : error ? (
          <tr>
            <td colSpan="7">
              <div className={styles.errorContainer}>
                <ShieldAlert size={18} color="var(--color-error)" />
                <span>Error: {error}</span>
              </div>
            </td>
          </tr>
        ) : (!logs || logs.length === 0) ? (
          <tr>
            <td colSpan="7">
              <div className={styles.emptyContainer}>
                <span>No audit logs recorded.</span>
              </div>
            </td>
          </tr>
        ) : (
          logs.map((log, index) => (
            <tr key={log.id}>
              <td className={styles.indexCell}>{startIndex + index + 1}</td>
              <td className={styles.timeCell}>{formatTimestamp(log.created_at)}</td>
              <td className={styles.actorCell}>
                <span className={styles.actorName}>
                  {log.actor?.name || (log.actor_id ? `User #${log.actor_id}` : 'System')}
                </span>
              </td>
              <td className={styles.actionBadgeCell}>
                {renderActionBadge(log.action)}
              </td>
              <td className={styles.targetCell}>
                <span className={styles.tableName}>{log.table_name}</span>
              </td>
              <td className={styles.ipCell}>
                <code>{log.ip_address || '-'}</code>
              </td>
              <td className={styles.action}>
                <div className={styles.actionGroup}>
                  <Button
                    className={styles.view}
                    onClick={() => onViewDetail(log)}
                    title="View payload changes"
                  >
                    <Eye strokeWidth={2.5} size={14} /> View
                  </Button>
                </div>
              </td>
            </tr>
          ))
        )}
      </tbody>
    </table>
  );
}
