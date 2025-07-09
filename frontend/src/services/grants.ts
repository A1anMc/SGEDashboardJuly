import { api } from './api';
import { Grant, GrantFilters, CreateGrantInput, UpdateGrantRequest } from '../types/models';

export interface GrantsResponse {
  items: Grant[];
  total: number;
  page: number;
  size: number;
}

export interface GrantDashboard {
  metrics: {
    total_active: number;
    total_value: number;
    success_rate: number;
    pending_applications: number;
  };
  status_distribution: Array<{
    name: string;
    value: number;
  }>;
  monthly_applications: Array<{
    month: string;
    applications: number;
  }>;
}

export interface ScraperRunRequest {
  sources?: string[];
  force_refresh?: boolean;
}

export interface ScraperStatus {
  status: string;
  last_run?: string;
  next_scheduled?: string;
  available_sources: string[];
  active_sources: string[];
  error_count: number;
  success_count: number;
}

export const grantsApi = {
  getGrants: async (filters?: GrantFilters) => {
    const response = await api.get<GrantsResponse>('/grants', { params: filters });
    return response.data;
  },

  getGrant: async (id: number) => {
    const response = await api.get<Grant>(`/grants/${id}`);
    return response.data;
  },

  createGrant: async (data: CreateGrantInput) => {
    const response = await api.post<Grant>('/grants', data);
    return response.data;
  },

  updateGrant: async (id: number, data: Partial<CreateGrantInput>) => {
    const response = await api.put<Grant>(`/grants/${id}`, data);
    return response.data;
  },

  deleteGrant: async (id: number) => {
    await api.delete(`/grants/${id}`);
  },

  runScraper: async () => {
    await api.post('/scraper/run');
  },

  getScraperStatus: async () => {
    const response = await api.get<ScraperStatus>('/scraper/status');
    return response.data;
  },

  runScrapers: async (request: ScraperRunRequest) => {
    const response = await api.post('/scraper/run', request);
    return response.data;
  },

  // New endpoints for managing grant sources
  getSources: async () => {
    const response = await api.get<string[]>('/grants/sources');
    return response.data;
  },

  getBySource: async (source: string, filters?: GrantFilters) => {
    const response = await api.get<GrantsResponse>(`/grants/source/${source}`, { params: filters });
    return response.data;
  },
}; 