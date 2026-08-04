import styles from './Pagination.module.css';
import { ChevronLeft, ChevronsLeft, ChevronRight , ChevronsRight } from 'lucide-react';

export default function Pagination({currentPage, totalPages, onPageChange, onBlur}) {
    return (
        <div className={styles.pagination}>
            <button
                disabled={currentPage <= 1}
                onClick={() => onPageChange(1)}
            >
                <ChevronsLeft size='20' />
            </button>
            <button 
                disabled={currentPage <= 1} 
                onClick={() => onPageChange(currentPage - 1)}
            >
                <ChevronLeft size='20' />
            </button>
            <span>
                <input 
                type="number"
                min="1"
                max={totalPages} 
                className={styles.pageInput} 
                value={currentPage} 
                onChange={(e) => onPageChange(e.target.value)} 
                onBlur={onBlur}
                />
                <span> / {totalPages}</span>
            </span>
            <button 
                disabled={currentPage >= totalPages} 
                onClick={() => onPageChange(currentPage + 1)}
            >
                <ChevronRight size='20' />
            </button>
            <button
                disabled={currentPage >= totalPages}
                onClick={() => onPageChange(totalPages)}
            >
                <ChevronsRight size='20' />
            </button>
        </div>
    );
}
                