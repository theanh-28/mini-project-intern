import styles from './CursorPagination.module.css';
import { ChevronLeft, ChevronRight, ChevronsLeft } from 'lucide-react';

export default function CursorPagination({
  currentPageIndex,
  hasPrev,
  hasNext,
  loading,
  onPrev,
  onNext,
  onFirst,
}) {
  return (
    <div className={styles.pagination}>
      {/* Nút về trang đầu tiên */}
      <button
        className={styles.pageBtn}
        disabled={!hasPrev || loading}
        onClick={onFirst || onPrev}
        title="First Page"
      >
        <ChevronsLeft size={18} />
      </button>

      {/* Nút lùi 1 trang */}
      <button
        className={styles.pageBtn}
        disabled={!hasPrev || loading}
        onClick={onPrev}
        title="Previous Page"
      >
        <ChevronLeft size={18} />
      </button>

      {/* Ô hiển thị trang hiện tại */}
      <div className={styles.pageDisplay}>
        <span className={styles.pageText}>Page {currentPageIndex + 1}</span>
      </div>

      {/* Nút trang tiếp theo */}
      <button
        className={styles.pageBtn}
        disabled={!hasNext || loading}
        onClick={onNext}
        title="Next Page"
      >
        <ChevronRight size={18} />
      </button>
    </div>
  );
}
