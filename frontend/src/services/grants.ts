import { api } from './api';
import { Grant, GrantFilters, GrantDashboard, GrantMatchResult, ProjectProfile, CreateGrantRequest, UpdateGrantRequest } from '@/types/models';

export interface GrantsResponse {
  items: Grant[];
  total: number;
  page: number;
  size: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface ScraperRunRequest {
  sources?: string[];
  force_refresh?: boolean;
}

export interface ScraperRunResponse {
  started_at: string;
  sources: string[];
  status: string;
  message: string;
}

export const grantsApi = {
  // Get paginated grants with filtering
  getGrants: async (filters?: GrantFilters): Promise<GrantsResponse> => {
    const params = new URLSearchParams();
    
    if (filters) {
      if (filters.industry_focus) params.append('industry_focus', filters.industry_focus);
      if (filters.location_eligibility) params.append('location_eligibility', filters.location_eligibility);
      if (filters.status) params.append('status', filters.status);
      if (filters.min_amount) params.append('min_amount', filters.min_amount.toString());
      if (filters.max_amount) params.append('max_amount', filters.max_amount.toString());
      if (filters.deadline_before) params.append('deadline_before', filters.deadline_before.toISOString());
      if (filters.deadline_after) params.append('deadline_after', filters.deadline_after.toISOString());
      if (filters.search) params.append('search', filters.search);
      if (filters.page) params.append('page', filters.page.toString());
      if (filters.size) params.append('size', filters.size.toString());
    }
    
    const response = await api.get<GrantsResponse>(`/grants?${params.toString()}`);
    return response.data;
  },

  // Get single grant
  getGrant: async (id: number): Promise<Grant> => {
    const response = await api.get<Grant>(`/grants/${id}`);
    return response.data;
  },

  // Create grant
  createGrant: async (grant: CreateGrantRequest): Promise<Grant> => {
    const response = await api.post<Grant>('/grants', grant);
    return response.data;
  },

  // Update grant
  updateGrant: async (id: number, grant: UpdateGrantRequest): Promise<Grant> => {
    const response = await api.put<Grant>(`/grants/${id}`, grant);
    return response.data;
  },

  // Delete grant
  deleteGrant: async (id: number): Promise<void> => {
    await api.delete(`/grants/${id}`);
  },

  // Match grants against project profile
  matchGrants: async (
    projectProfile: ProjectProfile,
    minScore: number = 60,
    limit: number = 10
  ): Promise<GrantMatchResult[]> => {
    const response = await api.post<GrantMatchResult[]>('/grants/match', projectProfile, {
      params: {
        min_score: minScore,
        limit
      }
    });
    return response.data;
  },

  // Get match details for specific grant
  getGrantMatchDetails: async (
    grantId: number,
    projectProfile: ProjectProfile
  ): Promise<GrantMatchResult> => {
    const response = await api.get<GrantMatchResult>(`/grants/${grantId}/match-details`, {
      params: projectProfile
    });
    return response.data;
  },

  // Get dashboard data
  getDashboard: async (): Promise<GrantDashboard> => {
    const response = await api.get<GrantDashboard>('/grants/dashboard/data');
    return response.data;
  },

  // Run scrapers
  runScrapers: async (request?: ScraperRunRequest): Promise<ScraperRunResponse> => {
    const response = await api.post<ScraperRunResponse>('/grants/scrape', request || {});
    return response.data;
  },

  // Get scraper status
  getScraperStatus: async () => {
    const response = await api.get('/grants/scrape/status');
    return response.data;
  }
};

// Legacy function for backwards compatibility
export const fetchGrantDashboard = async (): Promise<GrantDashboard> => {
  return grantsApi.getDashboard();
}; 