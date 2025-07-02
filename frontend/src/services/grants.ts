import { api } from './api';
import { Grant, GrantFilters } from '@/types/models';

export interface GrantsResponse {
  items: Grant[];
  total: number;
  page: number;
  size: number;
}

export interface GrantDashboard {
  metrics: {
    total_active: number;
    total_amount_available: number;
    upcoming_deadlines: number;
    avg_match_score: number;
  };
  categories: {
    by_industry: Record<string, number>;
    by_location: Record<string, number>;
    by_org_type: Record<string, number>;
    by_funding_range: Record<string, number>;
  };
  timeline: {
    this_week: DeadlineGroup;
    next_week: DeadlineGroup;
    this_month: DeadlineGroup;
    next_month: DeadlineGroup;
    later: DeadlineGroup;
  };
  matching_insights: {
    best_matches: Array<{
      grant_id: number;
      title: string;
      score: number;
    }>;
    common_mismatches: string[];
    suggested_improvements: string[];
  };
  last_updated: string;
}

interface DeadlineGroup {
  grants: Array<{
    id: number;
    title: string;
    deadline: string;
    amount: number;
  }>;
  total_amount: number;
  count: number;
}

export const grantsApi = {
  getGrants: async (filters?: GrantFilters) => {
    const response = await api.get<{ items: Grant[]; total: number }>('/grants', { params: filters });
    return response.data;
  },

  getGrant: async (id: number) => {
    const response = await api.get<Grant>(`/grants/${id}`);
    return response.data;
  },

  createGrant: async (data: Partial<Grant>) => {
    const response = await api.post<Grant>('/grants', data);
    return response.data;
  },

  updateGrant: async (id: number, data: Partial<Grant>) => {
    const response = await api.put<Grant>(`/grants/${id}`, data);
    return response.data;
  },

  deleteGrant: async (id: number) => {
    await api.delete(`/grants/${id}`);
  },

  getTags: async (): Promise<string[]> => {
    const { data } = await api.get('/grants/tags');
    return data;
  },

  runScraper: async () => {
    await api.post('/scraper/run');
  },
};

export const fetchGrantDashboard = async (): Promise<GrantDashboard> => {
  const response = await api.get<GrantDashboard>('/grants/dashboard');
  return response.data;
}; 