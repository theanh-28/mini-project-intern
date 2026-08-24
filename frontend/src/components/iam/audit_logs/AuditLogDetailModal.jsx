import { useState } from 'react';
import {
  X,
  Copy,
  Check,
  Clock,
  User,
  Globe,
  Database,
  ExternalLink,
  Code2,
  TableProperties,
  ArrowRight,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import styles from './AuditLogDetailModal.module.css';
import Button from '@/components/common/Button';
import Avatar from '@/components/common/Avatar';
import Spinner from '@/components/common/Spinner';
import { PATHS } from '@/constants/routes';

export default function AuditLogDetailModal({ log, loading, error, onClose }) {
  const [copied, setCopied] = useState(false);
  const [viewMode, setViewMode] = useState('visual'); // 'visual' | 'json'

  if (!log && !loading) return null;

  const handleCopyId = () => {
    if (log?.id) {
      navigator.clipboard.writeText(log.id);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getBadgeClass = (action) => {
    switch (action?.toUpperCase()) {
      case 'CREATE':
        return styles.badgeCreate;
      case 'UPDATE':
        return styles.badgeUpdate;
      case 'DELETE':
        return styles.badgeDelete;
      default:
        return styles.badgeDefault;
    }
  };

  // Trích xuất toàn bộ các trường dữ liệu thay đổi giữa old_value và new_value
  const getDiffKeys = () => {
    const oldKeys = Object.keys(log?.old_value || {});
    const newKeys = Object.keys(log?.new_value || {});
    return Array.from(new Set([...oldKeys, ...newKeys]));
  };

  const renderValue = (val, isOld = false) => {
    if (val === undefined || val === null) {
      return <span className={styles.emptyVal}>—</span>;
    }
    if (val === '[REDACTED]') {
      return <span className={styles.redactedVal}>•••••••• (Redacted)</span>;
    }
    if (typeof val === 'boolean') {
      return (
        <span className={val ? styles.boolTrue : styles.boolFalse}>
          {val ? 'true' : 'false'}
        </span>
      );
    }
    if (Array.isArray(val)) {
      return (
        <div className={styles.arrayWrapper}>
          {val.map((item, idx) => (
            <span key={idx} className={styles.arrayItem}>
              {String(item)}
            </span>
          ))}
        </div>
      );
    }
    if (typeof val === 'object') {
      return (
        <pre className={styles.nestedJson}>
          {JSON.stringify(val, null, 2)}
        </pre>
      );
    }
    return <span className={styles.textVal}>{String(val)}</span>;
  };

  const diffKeys = getDiffKeys();

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className={styles.header}>
          <div className={styles.headerTitleGroup}>
            <span className={`${styles.actionBadge} ${getBadgeClass(log?.action)}`}>
              {log?.action || 'ACTION'}
            </span>
            <h3 className={styles.title}>
              Audit Record: <span className={styles.highlight}>{log?.table_name}</span>
            </h3>
          </div>
          <button className={styles.closeBtn} onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {/* Modal Content */}
        <div className={styles.content}>
          {loading ? (
            <div className={styles.loadingContainer}>
              <Spinner />
              <p>Loading audit log details...</p>
            </div>
          ) : error ? (
            <div className={styles.errorContainer}>
              <p>Error: {error}</p>
            </div>
          ) : log ? (
            <>
              {/* Metadata Cards */}
              <div className={styles.metaGrid}>
                {/* Log ID */}
                <div className={styles.metaCard}>
                  <div className={styles.metaLabel}>
                    <Database size={14} /> Record ID
                  </div>
                  <div className={styles.idWrapper}>
                    <code className={styles.logId}>{log.id}</code>
                    <button className={styles.copyBtn} onClick={handleCopyId} title="Copy ID">
                      {copied ? <Check size={14} color="var(--color-success)" /> : <Copy size={14} />}
                    </button>
                  </div>
                </div>

                {/* Actor */}
                <div className={styles.metaCard}>
                  <div className={styles.metaLabel}>
                    <User size={14} /> Performed By
                  </div>
                  <div className={styles.actorRow}>
                    {log.actor ? (
                      <Link
                        to={`${PATHS.ADMIN_USERS}/${log.actor.user_id}`}
                        className={styles.actorLink}
                        title="View user profile"
                      >
                        <Avatar name={log.actor.name} size="sm" />
                        <div className={styles.actorText}>
                          <div className={styles.actorNameRow}>
                            <span className={styles.actorName}>{log.actor.name}</span>
                            <ExternalLink size={12} className={styles.extIcon} />
                          </div>
                          <span className={styles.actorEmail}>{log.actor.email}</span>
                        </div>
                      </Link>
                    ) : (
                      <span className={styles.systemActor}>System #{log.actor_id || '0'}</span>
                    )}
                  </div>
                </div>

                {/* Timestamp */}
                <div className={styles.metaCard}>
                  <div className={styles.metaLabel}>
                    <Clock size={14} /> Timestamp
                  </div>
                  <span className={styles.metaValue}>
                    {log.created_at ? new Date(log.created_at).toLocaleString('vi-VN') : '-'}
                  </span>
                </div>

                {/* IP Address */}
                <div className={styles.metaCard}>
                  <div className={styles.metaLabel}>
                    <Globe size={14} /> IP Address
                  </div>
                  <span className={styles.metaValue}>
                    <code>{log.ip_address || 'Unknown'}</code>
                  </span>
                </div>
              </div>

              {/* Data Changes Section */}
              <div className={styles.diffSection}>
                <div className={styles.diffHeaderBar}>
                  <h4 className={styles.diffTitle}>Payload Changes</h4>
                  <div className={styles.viewToggle}>
                    <button
                      className={`${styles.toggleBtn} ${viewMode === 'visual' ? styles.toggleActive : ''}`}
                      onClick={() => setViewMode('visual')}
                      title="Visual Table View"
                    >
                      <TableProperties size={14} />
                      <span>Visual Diff</span>
                    </button>
                    <button
                      className={`${styles.toggleBtn} ${viewMode === 'json' ? styles.toggleActive : ''}`}
                      onClick={() => setViewMode('json')}
                      title="Raw JSON View"
                    >
                      <Code2 size={14} />
                      <span>Raw JSON</span>
                    </button>
                  </div>
                </div>

                {viewMode === 'visual' ? (
                  /* Visual Table Diff */
                  diffKeys.length === 0 ? (
                    <div className={styles.emptyDiffBox}>
                      <span>No payload changes recorded.</span>
                    </div>
                  ) : (
                    <div className={styles.diffTableWrapper}>
                      <table className={styles.diffTable}>
                        <thead>
                          <tr>
                            <th style={{ width: '25%' }}>Field Name</th>
                            <th style={{ width: '37.5%' }}>Old Value</th>
                            <th style={{ width: '37.5%' }}>New Value</th>
                          </tr>
                        </thead>
                        <tbody>
                          {diffKeys.map((key) => {
                            const oldVal = log.old_value ? log.old_value[key] : undefined;
                            const newVal = log.new_value ? log.new_value[key] : undefined;
                            const isChanged = JSON.stringify(oldVal) !== JSON.stringify(newVal);

                            return (
                              <tr key={key} className={isChanged ? styles.rowChanged : ''}>
                                <td className={styles.fieldCell}>
                                  <code>{key}</code>
                                </td>
                                <td className={`${styles.valCell} ${oldVal !== undefined && isChanged ? styles.oldValCell : ''}`}>
                                  {renderValue(oldVal, true)}
                                </td>
                                <td className={`${styles.valCell} ${newVal !== undefined && isChanged ? styles.newValCell : ''}`}>
                                  {renderValue(newVal, false)}
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  )
                ) : (
                  /* Raw JSON Side-by-side */
                  <div className={styles.diffContainer}>
                    <div className={styles.diffBox}>
                      <div className={`${styles.diffBoxHeader} ${styles.oldHeader}`}>
                        <span>Previous State (Old Value)</span>
                      </div>
                      <pre className={`${styles.jsonCode} ${styles.oldJson}`}>
                        {log.old_value
                          ? JSON.stringify(log.old_value, null, 2)
                          : '(None - Record Created)'}
                      </pre>
                    </div>

                    <div className={styles.diffBox}>
                      <div className={`${styles.diffBoxHeader} ${styles.newHeader}`}>
                        <span>New State (New Value)</span>
                      </div>
                      <pre className={`${styles.jsonCode} ${styles.newJson}`}>
                        {log.new_value
                          ? JSON.stringify(log.new_value, null, 2)
                          : '(None - Record Deleted)'}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : null}
        </div>

        {/* Modal Footer */}
        <div className={styles.footer}>
          <Button className={styles.closeModalBtn} onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}
