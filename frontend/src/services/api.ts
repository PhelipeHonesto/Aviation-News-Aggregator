const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface NewsParams {
  source?: string;
  category?: string;
  limit?: number;
  offset?: number;
  q?: string;
}

interface IngestResponse {
  message: string;
  articles_fetched: number;
  articles_saved: number;
  status: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async getNews(params: NewsParams = {}) {
    const searchParams = new URLSearchParams();
    
    if (params.source) searchParams.append('source', params.source);
    if (params.category) searchParams.append('category', params.category);
    if (params.limit) searchParams.append('limit', params.limit.toString());
    if (params.offset) searchParams.append('offset', params.offset.toString());
    if (params.q) searchParams.append('q', params.q);

    const endpoint = `/news${searchParams.toString() ? `?${searchParams.toString()}` : ''}`;
    return this.request<import('../types').NewsResponse>(endpoint);
  }

  async searchNews(query: string) {
    const searchParams = new URLSearchParams({ q: query });
    return this.request<import('../types').SearchResponse>(`/search?${searchParams.toString()}`);
  }

  async getSources() {
    return this.request<import('../types').SourcesResponse>('/sources');
  }

  async ingestNews() {
    return this.request<IngestResponse>('/ingest', { method: 'POST' });
  }

  async healthCheck() {
    return this.request<{ status: string; timestamp: string }>('/health');
  }

  // Bookmark functions
  async addBookmark(articleId: number, userId: string = 'default') {
    return this.request<{ message: string }>(`/bookmarks/${articleId}?user_id=${userId}`, { 
      method: 'POST' 
    });
  }

  async removeBookmark(articleId: number, userId: string = 'default') {
    return this.request<{ message: string }>(`/bookmarks/${articleId}?user_id=${userId}`, { 
      method: 'DELETE' 
    });
  }

  async getBookmarks(userId: string = 'default', limit: number = 50) {
    return this.request<{ bookmarks: import('../types').Bookmark[] }>(`/bookmarks?user_id=${userId}&limit=${limit}`);
  }

  async checkBookmarkStatus(articleId: number, userId: string = 'default') {
    return this.request<{ bookmarked: boolean }>(`/bookmarks/${articleId}/status?user_id=${userId}`);
  }

  // Source health functions
  async getSourceHealth() {
    return this.request<{ sources: import('../types').SourceHealth[] }>('/sources/health');
  }
}

export const api = new ApiClient(API_BASE_URL);