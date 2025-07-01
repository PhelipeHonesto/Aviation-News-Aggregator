import type { Article } from '../types';
import type { FilterOptions } from '../components/SearchAndFilter';

/**
 * Filters and sorts articles based on the provided filter options
 */
export function filterAndSortArticles(
  articles: Article[],
  filters: FilterOptions
): Article[] {
  let filteredArticles = [...articles];

  // Apply search filter
  if (filters.search.trim()) {
    const searchTerm = filters.search.toLowerCase().trim();
    filteredArticles = filteredArticles.filter(article => {
      const title = article.title.toLowerCase();
      const body = (article.body || '').toLowerCase();
      const source = article.source.toLowerCase();
      
      return title.includes(searchTerm) || 
             body.includes(searchTerm) || 
             source.includes(searchTerm);
    });
  }

  // Apply status filter
  if (filters.status.length > 0) {
    filteredArticles = filteredArticles.filter(article =>
      filters.status.includes(article.status)
    );
  }

  // Apply source filter
  if (filters.sources.length > 0) {
    filteredArticles = filteredArticles.filter(article =>
      filters.sources.includes(article.source)
    );
  }

  // Apply date range filter
  if (filters.dateRange.start || filters.dateRange.end) {
    filteredArticles = filteredArticles.filter(article => {
      const articleDate = new Date(article.date);
      
      if (filters.dateRange.start) {
        const startDate = new Date(filters.dateRange.start);
        if (articleDate < startDate) return false;
      }
      
      if (filters.dateRange.end) {
        const endDate = new Date(filters.dateRange.end);
        endDate.setHours(23, 59, 59, 999); // Include the entire end day
        if (articleDate > endDate) return false;
      }
      
      return true;
    });
  }

  // Apply sorting
  filteredArticles.sort((a, b) => {
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

  return filteredArticles;
}

/**
 * Extracts unique sources from articles
 */
export function getUniqueSources(articles: Article[]): string[] {
  const sources = new Set(articles.map(article => article.source));
  return Array.from(sources).sort();
}

/**
 * Gets status distribution for articles
 */
export function getStatusDistribution(articles: Article[]): Record<string, number> {
  return articles.reduce((acc, article) => {
    acc[article.status] = (acc[article.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
}

/**
 * Checks if an article matches the current filters
 */
export function articleMatchesFilters(
  article: Article,
  filters: FilterOptions
): boolean {
  // Search filter
  if (filters.search.trim()) {
    const searchTerm = filters.search.toLowerCase().trim();
    const title = article.title.toLowerCase();
    const body = (article.body || '').toLowerCase();
    const source = article.source.toLowerCase();
    
    if (!title.includes(searchTerm) && 
        !body.includes(searchTerm) && 
        !source.includes(searchTerm)) {
      return false;
    }
  }

  // Status filter
  if (filters.status.length > 0 && !filters.status.includes(article.status)) {
    return false;
  }

  // Source filter
  if (filters.sources.length > 0 && !filters.sources.includes(article.source)) {
    return false;
  }

  // Date range filter
  if (filters.dateRange.start || filters.dateRange.end) {
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
  }

  return true;
}

/**
 * Highlights search terms in text
 */
export function highlightSearchTerm(text: string, searchTerm: string): string {
  if (!searchTerm.trim()) return text;
  
  const regex = new RegExp(`(${searchTerm})`, 'gi');
  return text.replace(regex, '<mark>$1</mark>');
}

/**
 * Gets filter summary for display
 */
export function getFilterSummary(filters: FilterOptions): string[] {
  const summary: string[] = [];
  
  if (filters.search) {
    summary.push(`Search: "${filters.search}"`);
  }
  
  if (filters.status.length > 0) {
    summary.push(`Status: ${filters.status.join(', ')}`);
  }
  
  if (filters.sources.length > 0) {
    summary.push(`Sources: ${filters.sources.join(', ')}`);
  }
  
  if (filters.dateRange.start || filters.dateRange.end) {
    const dateRange = [];
    if (filters.dateRange.start) dateRange.push(`From: ${filters.dateRange.start}`);
    if (filters.dateRange.end) dateRange.push(`To: ${filters.dateRange.end}`);
    summary.push(`Date: ${dateRange.join(' - ')}`);
  }
  
  summary.push(`Sort: ${filters.sortBy} (${filters.sortOrder})`);
  
  return summary;
} 