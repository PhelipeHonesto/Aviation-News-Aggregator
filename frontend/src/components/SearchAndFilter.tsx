import { useState, useEffect, useCallback } from 'react';
import './SearchAndFilter.css';

export interface FilterOptions {
  search: string;
  status: string[];
  sources: string[];
  dateRange: {
    start: string;
    end: string;
  };
  sortBy: 'date' | 'title' | 'source';
  sortOrder: 'asc' | 'desc';
}

interface SearchAndFilterProps {
  onFilterChange: (filters: FilterOptions) => void;
  onSearchChange?: (query: string) => void;
  availableSources: string[];
  totalArticles: number;
  filteredCount: number;
}

const SearchAndFilter = ({ 
  onFilterChange, 
  onSearchChange,
  availableSources, 
  totalArticles, 
  filteredCount 
}: SearchAndFilterProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [filters, setFilters] = useState<FilterOptions>({
    search: '',
    status: [],
    sources: [],
    dateRange: {
      start: '',
      end: ''
    },
    sortBy: 'date',
    sortOrder: 'desc'
  });

  const statusOptions = [
    { value: 'new', label: 'New', color: '#6c757d' },
    { value: 'selected', label: 'Selected', color: '#f17500' },
    { value: 'edited', label: 'Edited', color: '#0a4bb6' },
    { value: 'posted', label: 'Posted', color: '#28a745' }
  ];

  const sortOptions = [
    { value: 'date', label: 'Date' },
    { value: 'title', label: 'Title' },
    { value: 'source', label: 'Source' }
  ];

  // Debounced filter update
  const debouncedFilterUpdate = useCallback(
    debounce((newFilters: FilterOptions) => {
      onFilterChange(newFilters);
    }, 300),
    [onFilterChange]
  );

  useEffect(() => {
    debouncedFilterUpdate(filters);
  }, [filters, debouncedFilterUpdate]);

  const updateFilters = (updates: Partial<FilterOptions>) => {
    setFilters(prev => ({ ...prev, ...updates }));
  };

  const handleStatusToggle = (status: string) => {
    setFilters(prev => ({
      ...prev,
      status: prev.status.includes(status)
        ? prev.status.filter(s => s !== status)
        : [...prev.status, status]
    }));
  };

  const handleSourceToggle = (source: string) => {
    setFilters(prev => ({
      ...prev,
      sources: prev.sources.includes(source)
        ? prev.sources.filter(s => s !== source)
        : [...prev.sources, source]
    }));
  };

  const clearAllFilters = () => {
    setFilters({
      search: '',
      status: [],
      sources: [],
      dateRange: {
        start: '',
        end: ''
      },
      sortBy: 'date',
      sortOrder: 'desc'
    });
  };

  const hasActiveFilters = filters.search || 
    filters.status.length > 0 || 
    filters.sources.length > 0 || 
    filters.dateRange.start || 
    filters.dateRange.end;

  return (
    <div className="search-and-filter">
      {/* Main Search Bar */}
      <div className="search-bar">
        <div className="search-input-container">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search articles by title, content, or source..."
            value={filters.search}
            onChange={(e) => {
              updateFilters({ search: e.target.value });
              onSearchChange?.(e.target.value);
            }}
            className="search-input"
          />
          {filters.search && (
            <button
              onClick={() => updateFilters({ search: '' })}
              className="clear-search-btn"
            >
              ×
            </button>
          )}
        </div>
        
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className={`expand-filters-btn ${isExpanded ? 'expanded' : ''}`}
        >
          {isExpanded ? 'Hide Filters' : 'Show Filters'}
        </button>
      </div>

      {/* Filter Summary */}
      {hasActiveFilters && (
        <div className="filter-summary">
          <span className="filter-count">
            Showing {filteredCount} of {totalArticles} articles
          </span>
          <button onClick={clearAllFilters} className="clear-filters-btn">
            Clear All Filters
          </button>
        </div>
      )}

      {/* Expanded Filters */}
      {isExpanded && (
        <div className="filters-panel">
          <div className="filters-grid">
            {/* Status Filters */}
            <div className="filter-section">
              <h3>Status</h3>
              <div className="filter-chips">
                {statusOptions.map(option => (
                  <button
                    key={option.value}
                    onClick={() => handleStatusToggle(option.value)}
                    className={`filter-chip ${filters.status.includes(option.value) ? 'active' : ''}`}
                    style={{
                      '--chip-color': option.color
                    } as React.CSSProperties}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Source Filters */}
            {availableSources.length > 0 && (
              <div className="filter-section">
                <h3>Sources</h3>
                <div className="filter-chips">
                  {availableSources.slice(0, 8).map(source => (
                    <button
                      key={source}
                      onClick={() => handleSourceToggle(source)}
                      className={`filter-chip ${filters.sources.includes(source) ? 'active' : ''}`}
                    >
                      {source}
                    </button>
                  ))}
                  {availableSources.length > 8 && (
                    <span className="more-sources">
                      +{availableSources.length - 8} more
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Date Range */}
            <div className="filter-section">
              <h3>Date Range</h3>
              <div className="date-range">
                <div className="date-input-group">
                  <label>From:</label>
                  <input
                    type="date"
                    value={filters.dateRange.start}
                    onChange={(e) => updateFilters({
                      dateRange: { ...filters.dateRange, start: e.target.value }
                    })}
                    className="date-input"
                  />
                </div>
                <div className="date-input-group">
                  <label>To:</label>
                  <input
                    type="date"
                    value={filters.dateRange.end}
                    onChange={(e) => updateFilters({
                      dateRange: { ...filters.dateRange, end: e.target.value }
                    })}
                    className="date-input"
                  />
                </div>
              </div>
            </div>

            {/* Sort Options */}
            <div className="filter-section">
              <h3>Sort By</h3>
              <div className="sort-controls">
                <select
                  value={filters.sortBy}
                  onChange={(e) => updateFilters({ sortBy: e.target.value as any })}
                  className="sort-select"
                >
                  {sortOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                <button
                  onClick={() => updateFilters({
                    sortOrder: filters.sortOrder === 'asc' ? 'desc' : 'asc'
                  })}
                  className="sort-order-btn"
                >
                  {filters.sortOrder === 'asc' ? '↑' : '↓'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Debounce utility function
function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

export default SearchAndFilter; 
