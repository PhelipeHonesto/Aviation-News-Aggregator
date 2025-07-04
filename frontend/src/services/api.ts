import type { Article } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({})); // Catch if the error body is not JSON
    const errorMessage = errorData.detail || `HTTP error! status: ${response.status}`;
    throw new Error(errorMessage);
  }
  return response.json();
};

export const getNews = async (): Promise<Article[]> => {
  const response = await fetch(`${API_BASE_URL}/news`);
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

export const postToSlack = async (storyId: string) => {
  const response = await fetch(`${API_BASE_URL}/slack/${storyId}`, { method: 'POST' });
  return handleResponse(response);
};
