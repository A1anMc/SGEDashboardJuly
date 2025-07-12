import { api } from './api';
import { Grant, GrantFilters, CreateGrantInput, UpdateGrantRequest } from '../types/models';

// Constants for API endpoints
const ENDPOINTS = {
  BASE: '/grants/',
  SCRAPER_RUN: '/grants/scrape/',
  SCRAPER_STATUS: '/scraper/sources/',
  SOURCES: '/grants/sources/',
} as const;

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
    const response = await api.get<GrantsResponse>(ENDPOINTS.BASE, { 
      params: filters,
      // Add error handling specific to grants
      validateStatus: (status) => status < 500,
    });
    return response.data;
  },

  getGrant: async (id: number) => {
    const response = await api.get<Grant>(`${ENDPOINTS.BASE}/${id}`);
    return response.data;
  },

  createGrant: async (data: CreateGrantInput) => {
    const response = await api.post<Grant>(ENDPOINTS.BASE, data);
    return response.data;
  },

  updateGrant: async (id: number, data: Partial<CreateGrantInput>) => {
    const response = await api.put<Grant>(`${ENDPOINTS.BASE}/${id}`, data);
    return response.data;
  },

  deleteGrant: async (id: number) => {
    await api.delete(`${ENDPOINTS.BASE}/${id}`);
  },

  runScraper: async () => {
    await api.post(ENDPOINTS.SCRAPER_RUN);
  },

  getScraperStatus: async (): Promise<ScraperStatus> => {
    const response = await api.get(ENDPOINTS.SCRAPER_STATUS);
    // Transform the array response to match the expected format
    const sources = response.data || [];
    const totalSources = sources.length;
    const successfulSources = sources.filter((s: any) => s.status === 'success').length;
    const errorSources = sources.filter((s: any) => s.status === 'error').length;
    
    return {
      status: totalSources > 0 ? (successfulSources > 0 ? 'active' : 'error') : 'inactive',
      available_sources: sources.map((s: any) => s.source_name),
      active_sources: sources.filter((s: any) => s.status === 'success').map((s: any) => s.source_name),
      last_run: sources.length > 0 ? sources[0].last_run : null,
      next_scheduled: sources.length > 0 ? sources[0].next_scheduled : undefined,
      success_count: successfulSources,
      error_count: errorSources
    };
  },

  runScrapers: async (request: ScraperRunRequest) => {
    const response = await api.post(ENDPOINTS.SCRAPER_RUN, request);
    return response.data;
  },

  // New endpoints for managing grant sources
  getSources: async () => {
    const response = await api.get<string[]>(ENDPOINTS.SOURCES);
    return response.data;
  },

  getBySource: async (source: string, filters?: GrantFilters) => {
    const response = await api.get<GrantsResponse>(`${ENDPOINTS.BASE}/source/${source}`, { 
      params: filters,
      validateStatus: (status) => status < 500,
    });
    return response.data;
  },
}; 