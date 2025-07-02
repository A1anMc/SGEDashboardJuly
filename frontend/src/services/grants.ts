import { api } from './api';

export interface Grant {
  id: number;
  title: string;
  description: string;
  amount: number;
  deadline: string;
  status: 'open' | 'closed' | 'draft';
  tags: string[];
  source_url?: string;
  created_at: string;
  updated_at: string;
}

export interface GrantsResponse {
  items: Grant[];
  total: number;
  page: number;
  size: number;
}

export interface GrantFilters {
  status?: string;
  tags?: string[];
  search?: string;
  page?: number;
  size?: number;
}

export const grantsApi = {
  // Get all grants with pagination and filters
  getGrants: async (filters: GrantFilters = {}): Promise<GrantsResponse> => {
    const { data } = await api.get('/grants', { params: filters });
    return data;
  },

  // Get a single grant by ID
  getGrant: async (id: number): Promise<Grant> => {
    const { data } = await api.get(`/grants/${id}`);
    return data;
  },

  // Create a new grant
  createGrant: async (grant: Partial<Grant>): Promise<Grant> => {
    const { data } = await api.post('/grants', grant);
    return data;
  },

  // Update an existing grant
  updateGrant: async (id: number, grant: Partial<Grant>): Promise<Grant> => {
    const { data } = await api.put(`/grants/${id}`, grant);
    return data;
  },

  // Delete a grant
  deleteGrant: async (id: number): Promise<void> => {
    await api.delete(`/grants/${id}`);
  },

  // Get all available tags
  getTags: async (): Promise<string[]> => {
    const { data } = await api.get('/grants/tags');
    return data;
  },

  // Run the grant scraper
  runScraper: async (): Promise<void> => {
    await api.post('/scraper/run');
  },
}; 