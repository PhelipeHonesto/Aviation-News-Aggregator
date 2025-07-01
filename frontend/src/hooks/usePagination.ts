import { useState, useMemo, useCallback } from 'react';
import type { Article } from '../types';
import type { FilterOptions } from '../components/SearchAndFilter';

export type PaginationMode = 'infinite' | 'pagination' | 'load-more';

interface UsePaginationOptions {
  mode: PaginationMode;
  itemsPerPage?: number;
  initialPage?: number;
}

interface UsePaginationReturn {
  // Current state
  currentPage: number;
  currentItems: Article[];
  hasMore: boolean;
  isLoading: boolean;
  
  // Pagination info
  totalPages: number;
  totalItems: number;
  itemsPerPage: number;
  
  // Actions
  loadMore: () => Promise<void>;
  goToPage: (page: number) => void;
  resetPagination: () => void;
  
  // Utility
  startIndex: number;
  endIndex: number;
}

export function usePagination(
  allItems: Article[],
  filters: FilterOptions,
  options: UsePaginationOptions
): UsePaginationReturn {
  const { mode, itemsPerPage: initialItemsPerPage = 20, initialPage = 1 } = options;
  
  // State
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [isLoading, setIsLoading] = useState(false);
  const [loadedItems, setLoadedItems] = useState<Article[]>([]);
  
  // Memoized values
  const filteredItems = useMemo(() => {
    // Apply filters first
    let filtered = [...allItems];
    
    // Search filter
    if (filters.search.trim()) {
      const searchTerm = filters.search.toLowerCase().trim();
      filtered = filtered.filter(article => {
        const title = article.title.toLowerCase();
        const body = (article.body || '').toLowerCase();
        const source = article.source.toLowerCase();
        
        return title.includes(searchTerm) || 
               body.includes(searchTerm) || 
               source.includes(searchTerm);
      });
    }
    
    // Status filter
    if (filters.status.length > 0) {
      filtered = filtered.filter(article =>
        filters.status.includes(article.status)
      );
    }
    
    // Source filter
    if (filters.sources.length > 0) {
      filtered = filtered.filter(article =>
        filters.sources.includes(article.source)
      );
    }
    
    // Date range filter
    if (filters.dateRange.start || filters.dateRange.end) {
      filtered = filtered.filter(article => {
        const articleDate = new Date(article.date);
        
        if (filters.dateRange.start) {
          const startDate = new Date(filters.dateRange.start);
          if (articleDate < startDate) return false;
        }
        
        if (filters.dateRange.end) {
          const endDate = new Date(filters.dateRange.end);
          endDate.setHours(23, 59, 59, 999);
          if (articleDate > endDate) return false;
        }
        
        return true;
      });
    }
    
    // Apply sorting
    filtered.sort((a, b) => {
      let comparison = 0;
      
      switch (filters.sortBy) {
        case 'date':
          comparison = new Date(a.date).getTime() - new Date(b.date).getTime();
          break;
        case 'title':
          comparison = a.title.localeCompare(b.title);
          break;
        case 'source':
          comparison = a.source.localeCompare(b.source);
          break;
        default:
          comparison = 0;
      }
      
      return filters.sortOrder === 'asc' ? comparison : -comparison;
    });
    
    return filtered;
  }, [allItems, filters]);
  
  const totalItems = filteredItems.length;
  const totalPages = Math.ceil(totalItems / initialItemsPerPage);
  
  // Calculate current items based on mode
  const currentItems = useMemo(() => {
    switch (mode) {
      case 'infinite':
      case 'load-more':
        return loadedItems;
      case 'pagination':
        const start = (currentPage - 1) * initialItemsPerPage;
        const end = start + initialItemsPerPage;
        return filteredItems.slice(start, end);
      default:
        return [];
    }
  }, [mode, loadedItems, currentPage, filteredItems, initialItemsPerPage]);
  
  const hasMore = useMemo(() => {
    switch (mode) {
      case 'infinite':
      case 'load-more':
        return loadedItems.length < filteredItems.length;
      case 'pagination':
        return currentPage < totalPages;
      default:
        return false;
    }
  }, [mode, loadedItems.length, filteredItems.length, currentPage, totalPages]);
  
  const startIndex = useMemo(() => {
    switch (mode) {
      case 'infinite':
      case 'load-more':
        return 0;
      case 'pagination':
        return (currentPage - 1) * initialItemsPerPage;
      default:
        return 0;
    }
  }, [mode, currentPage, initialItemsPerPage]);
  
  const endIndex = useMemo(() => {
    return startIndex + currentItems.length;
  }, [startIndex, currentItems.length]);
  
  // Actions
  const loadMore = useCallback(async () => {
    if (isLoading || !hasMore) return;
    
    setIsLoading(true);
    
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      if (mode === 'infinite' || mode === 'load-more') {
        const currentLength = loadedItems.length;
        const newItems = filteredItems.slice(currentLength, currentLength + initialItemsPerPage);
        setLoadedItems(prev => [...prev, ...newItems]);
      }
    } catch (error) {
      console.error('Error loading more items:', error);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, hasMore, mode, loadedItems.length, filteredItems, initialItemsPerPage]);
  
  const goToPage = useCallback((page: number) => {
    if (page >= 1 && page <= totalPages && page !== currentPage) {
      setCurrentPage(page);
    }
  }, [currentPage, totalPages]);
  
  const resetPagination = useCallback(() => {
    setCurrentPage(initialPage);
    setLoadedItems([]);
  }, [initialPage]);
  
  // Reset pagination when filters change
  useMemo(() => {
    resetPagination();
  }, [filters, resetPagination]);
  
  return {
    currentPage,
    currentItems,
    hasMore,
    isLoading,
    totalPages,
    totalItems,
    itemsPerPage: initialItemsPerPage,
    loadMore,
    goToPage,
    resetPagination,
    startIndex,
    endIndex
  };
} 