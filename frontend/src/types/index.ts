export interface Article {
  id: string;
  source: string;
  title: string;
  url: string;
  published_at: string;
  summary?: string;
  category?: string;
  fetched_at: string;
}

export interface NewsResponse {
  articles: Article[];
  total: number;
  filters?: {
    source?: string;
    category?: string;
  };
}

export interface SearchResponse {
  articles: Article[];
  query: string;
  total: number;
}

export interface SourcesResponse {
  sources: string[];
}

export interface Bookmark {
  id: number;
  article_id: number;
  user_id: string;
  created_at: string;
  article_title: string;
  article_source: string;
  article_url: string;
  article_published_at: string;
  article_summary?: string;
  article_category?: string;
}

export interface SourceHealth {
  name: string;
  category: string;
  kind: string;
  weight: number;
  enabled: boolean;
  success_24h: number;
  fail_24h: number;
  reliability_score: number;
  last_ok_at: string | null;
  error_streak: number;
  disabled_reason: string | null;
  last_error: string | null;
}