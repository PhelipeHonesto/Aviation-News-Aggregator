import { create } from 'zustand';
import type { Article } from '../types';

interface ArticleState {
  articles: Article[];
  setArticles: (articles: Article[]) => void;
}

export const useArticleStore = create<ArticleState>((set) => ({
  articles: [],
  setArticles: (articles) => set({ articles }),
})); 