import type { Article } from '../types';

export interface SocialDraft {
  id: string;
  article_id: string;
  hook: string;
  bullets: string[];
  why: string;
  caption: string;
  alt_text: string;
  tags: string[];
  attribution: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface SocialDraftIn {
  tone?: string;
  max_bullets?: number;
}

export interface SocialDraftUpdate {
  hook?: string;
  bullets?: string[];
  why?: string;
  caption?: string;
  alt_text?: string;
  tags?: string[];
  attribution?: string;
  status?: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    let errorMessage = `API ${response.status}: ${response.statusText}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      // If response is not JSON, try to get text
      try {
        const errorText = await response.text();
        errorMessage = errorText || errorMessage;
      } catch {
        // Keep the default error message
      }
    }
    throw new Error(errorMessage);
  }
  return response.json();
};

export interface NewsResponse {
  articles: Article[];
  pagination: {
    page: number;
    page_size: number;
    total_count: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

export interface NewsParams {
  q?: string;
  source?: string;
  status?: string;
  category?: string;
  page?: number;
  page_size?: number;
  sort_by?: 'published_at' | 'score' | 'created_at';
  sort_order?: 'asc' | 'desc';
}

export const getNews = async (params: NewsParams = {}): Promise<NewsResponse> => {
  const searchParams = new URLSearchParams();
  
  if (params.q) searchParams.append('q', params.q);
  if (params.source) searchParams.append('source', params.source);
  if (params.status) searchParams.append('status', params.status);
  if (params.category) searchParams.append('category', params.category);
  if (params.page) searchParams.append('page', params.page.toString());
  if (params.page_size) searchParams.append('page_size', params.page_size.toString());
  if (params.sort_by) searchParams.append('sort_by', params.sort_by);
  if (params.sort_order) searchParams.append('sort_order', params.sort_order);
  
  const url = `${API_BASE_URL}/news${searchParams.toString() ? `?${searchParams.toString()}` : ''}`;
  const response = await fetch(url);
  return handleResponse(response);
};

export const ingestNews = async () => {
  const response = await fetch(`${API_BASE_URL}/ingest`, { method: 'POST' });
  return handleResponse(response);
};

export const selectStory = async (storyId: string) => {
  const response = await fetch(`${API_BASE_URL}/select/${storyId}`, { method: 'POST' });
  return handleResponse(response);
};

export const editStory = async (storyId: string) => {
  const response = await fetch(`${API_BASE_URL}/edit/${storyId}`, { method: 'POST' });
  return handleResponse(response);
};

export const exportStory = async (storyId: string) => {
  const response = await fetch(`${API_BASE_URL}/export/${storyId}`, { method: 'POST' });
  return handleResponse(response);
};

export const getStats = async () => {
  const response = await fetch(`${API_BASE_URL}/stats`);
  return handleResponse(response);
};

// Social Draft API functions
export const createSocialDraft = async (articleId: string, data: SocialDraftIn): Promise<SocialDraft> => {
  const response = await fetch(`${API_BASE_URL}/articles/${articleId}/social-draft`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return handleResponse(response);
};

export const getSocialDraft = async (articleId: string): Promise<SocialDraft> => {
  const response = await fetch(`${API_BASE_URL}/articles/${articleId}/social-draft`);
  return handleResponse(response);
};

export const updateSocialDraft = async (draftId: string, data: SocialDraftUpdate): Promise<SocialDraft> => {
  const response = await fetch(`${API_BASE_URL}/social-drafts/${draftId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return handleResponse(response);
};

export const approveSocialDraft = async (draftId: string) => {
  const response = await fetch(`${API_BASE_URL}/social-drafts/${draftId}/approve`, {
    method: 'POST'
  });
  return handleResponse(response);
};

export const markSocialDraftPosted = async (draftId: string) => {
  const response = await fetch(`${API_BASE_URL}/social-drafts/${draftId}/post`, {
    method: 'POST'
  });
  return handleResponse(response);
};

// Content Factory API
export const selectArticle = async (articleId: string): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/content/articles/${articleId}/select`, {
    method: 'POST',
  });
  return handleResponse(response);
};

export const createContentDraft = async (articleId: string, platform: string): Promise<SocialDraft> => {
  const response = await fetch(`${API_BASE_URL}/content/articles/${articleId}/draft?platform=${platform}`, {
    method: 'POST',
  });
  return handleResponse(response);
};

export const updateDraft = async (draftId: string, draftData: any): Promise<SocialDraft> => {
  const response = await fetch(`${API_BASE_URL}/content/drafts/${draftId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(draftData),
  });
  return handleResponse(response);
};

export const approveDraft = async (draftId: string): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/content/drafts/${draftId}/approve`, {
    method: 'POST',
  });
  return handleResponse(response);
};

export const exportDraft = async (draftId: string, platform: string): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/content/drafts/${draftId}/export?fmt=${platform}`, {
    method: 'POST',
  });
  return handleResponse(response);
};

export const getInbox = async (): Promise<{ articles: Article[] }> => {
  const response = await fetch(`${API_BASE_URL}/content/inbox`);
  return handleResponse(response);
};

export const getDrafts = async (): Promise<{ drafts: SocialDraft[] }> => {
  const response = await fetch(`${API_BASE_URL}/content/drafts`);
  return handleResponse(response);
};

export const getExports = async (): Promise<{ exports: SocialDraft[] }> => {
  const response = await fetch(`${API_BASE_URL}/content/exports`);
  return handleResponse(response);
};

// Grouped API object for easier imports
export const api = {
  // News API
  getNews,
  ingestNews,
  selectStory,
  editStory,
  exportStory,
  getStats,
  
  // Social Draft API
  createSocialDraft,
  getSocialDraft,
  updateSocialDraft,
  approveSocialDraft,
  markSocialDraftPosted,
  
  // Content Factory API
  selectArticle,
  createContentDraft,
  updateDraft,
  approveDraft,
  exportDraft,
  getInbox,
  getDrafts,
  getExports,
};
