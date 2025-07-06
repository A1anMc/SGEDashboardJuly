import { api } from './api';
import { Grant, GrantFilters, CreateGrantInput } from '@/types/models';

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

export const grantsApi = {
  getGrants: async (filters?: GrantFilters) => {
    const response = await api.get<GrantsResponse>('/grants', { params: filters });
    return response.data;
  },

  getGrant: async (id: string) => {
    const response = await api.get<Grant>(`/grants/${id}`);
    return response.data;
  },

  createGrant: async (data: CreateGrantInput) => {
    const response = await api.post<Grant>('/grants', data);
    return response.data;
  },

  updateGrant: async (id: string, data: CreateGrantInput) => {
    const response = await api.put<Grant>(`/grants/${id}`, data);
    return response.data;
  },

  deleteGrant: async (id: string) => {
    await api.delete(`/grants/${id}`);
  },

  runScraper: async () => {
    await api.post('/scraper/run');
  },
}; 