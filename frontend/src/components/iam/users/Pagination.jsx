import styles from './Pagination.module.css';
import { ChevronLeft, ChevronsLeft, ChevronRight, ChevronsRight } from 'lucide-react';
import { usePagination } from '@/hooks/usePagination';

export default function Pagination({ currentPage, totalPages, onPageChange }) {
    const {
        inputValue,
        handleInputChange,
        handleKeyDown,
        handleBlur,
        handleButtonClick,
    } = usePagination({ currentPage, totalPages, onPageChange });

    return (
        <div className={styles.pagination}>
            <button
                className={styles.pageBtn}
                disabled={currentPage <= 1}
                onClick={() => handleButtonClick(1)}
                title="First Page"
            >
                <ChevronsLeft size={18} />
            </button>
            <button 
                className={styles.pageBtn}
                disabled={currentPage <= 1} 
                onClick={() => handleButtonClick(currentPage - 1)}
                title="Previous Page"
            >
                <ChevronLeft size={18} />
            </button>

            <div className={styles.pageDisplay}>
                <input 
                    type="number"
                    min="1"
                    max={totalPages} 
                    className={styles.pageInput} 
                    value={inputValue} 
                    onChange={handleInputChange} 
                    onKeyDown={handleKeyDown}
                    onBlur={handleBlur}
                />
                <span className={styles.totalPagesText}>/ {totalPages}</span>
            </div>

            <button 
                className={styles.pageBtn}
                disabled={currentPage >= totalPages} 
                onClick={() => handleButtonClick(currentPage + 1)}
                title="Next Page"
            >
                <ChevronRight size={18} />
            </button>
            <button
                className={styles.pageBtn}
                disabled={currentPage >= totalPages}
                onClick={() => handleButtonClick(totalPages)}
                title="Last Page"
            >
                <ChevronsRight size={18} />
            </button>
        </div>
    );
}
                