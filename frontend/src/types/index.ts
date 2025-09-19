// frontend/src/types/index.ts
export type Article = {
  id: number;
  title: string;
  url: string;
  canonical_url?: string | null;
  source: string;
  summary?: string | null;
  published_at?: string | null;   // optional in API
  fetched_at?: string | null;     // handy fallback if you have it
  score?: number;
};

export type Bookmark = {
  id: number;
  article_id: number;
  user_id: string;
  created_at: string;
  article_title: string;
  article_source: string;
  article_url: string;
  article_published_at: string;
  article_summary?: string | null;
};

export type SourceHealth = {
  name: string;
  enabled: boolean;
  success_24h: number;
  fail_24h: number;
  last_ok_at?: string | null;
  disabled_reason?: string | null;

  // Add these because the UI references them:
  error_streak?: number;          // may be undefined
  last_error?: string | null;     // missing in your build
  reliability_score?: number;     // may be undefined
};

export type NewsResponse = {
  articles: Article[];
  next_cursor?: string | null;
};

export type SourcesResponse = {
  sources: SourceHealth[];
};

export type BookmarksResponse = {
  bookmarks: Bookmark[];
};

export type HealthResponse = {
  status: "ok";
  uptime_seconds: number;
};

export type SourceActivity = {
  articles_last_hour: number;
  articles_last_24h: number;
  avg_articles_per_hour: number;
  last_article_at?: string | null;
  optimal_interval_minutes: number;
  priority_score: number;
  enabled: boolean;
};

export type RankingStats = {
  source_rankings: Record<string, {
    count: number;
    total_score: number;
    avg_score: number;
    top_score: number;
    authority_score: number;
  }>;
  duplicate_groups: number;
  total_articles_analyzed: number;
};

export type YouTubeChannel = {
  name: string;
  channel_id: string;
  category: string;
  priority: number;
  enabled: boolean;
  info?: {
    description: string;
    subscriber_count: number;
    video_count: number;
  } | null;
};

export type IngestResponse = {
  message: string;
  articles_saved: number;
  status: string;
};

export type SourceToggleResponse = {
  message: string;
};

export type SearchResponse = {
  articles: Article[];
  query: string;
  total_count?: number;
};

// API Error types
export type ApiError = {
  detail: string;
  status_code: number;
  error_type?: string;
};

// Component props types
export type NewsTerminalProps = {};

export type ArticleCardProps = {
  article: Article;
  isBookmarked?: boolean;
  onBookmarkToggle?: (articleId: number) => void;
};

export type SourceListProps = {
  sources: string[];
  selectedSource?: string;
  onSourceSelect?: (source: string) => void;
};

export type BookmarkListProps = {
  bookmarks: Bookmark[];
  onRemoveBookmark?: (bookmarkId: number) => void;
};