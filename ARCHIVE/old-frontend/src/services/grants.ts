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
    try {
      console.log('[grantsApi.getGrants] Starting with filters:', filters);

      // Transform pagination parameters from page/size to skip/limit
      const apiParams: any = filters ? {
        ...filters,
        skip: filters.page ? (filters.page - 1) * filters.size : 0,
        limit: filters.size || 10,
      } : {
        skip: 0,
        limit: 10,
      };
      
      // Remove the page and size parameters since API uses skip/limit
      if (apiParams.page) delete apiParams.page;
      if (apiParams.size) delete apiParams.size;

      console.log('[grantsApi.getGrants] Transformed API params:', apiParams);
      console.log('[grantsApi.getGrants] Making request to:', ENDPOINTS.BASE);
      console.log('[grantsApi.getGrants] Full URL will be:', `${api.defaults.baseURL}${ENDPOINTS.BASE}`);
      
      // Try axios first, then fallback to fetch
      let response;
      try {
        console.log('[grantsApi.getGrants] Attempting axios request...');
        response = await api.get<GrantsResponse>(ENDPOINTS.BASE, { 
          params: apiParams,
        });
        console.log('[grantsApi.getGrants] Axios request successful:', response.status);
      } catch (axiosError) {
        console.warn('[grantsApi.getGrants] Axios failed, trying fetch fallback:', axiosError);
        
        // Fallback to direct fetch
        const queryString = new URLSearchParams(apiParams).toString();
        const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const url = `${baseURL}/api/v1/grants/?${queryString}`;
        
        console.log('[grantsApi.getGrants] Attempting fetch to:', url);
        
        const fetchResponse = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
        });
        
        console.log('[grantsApi.getGrants] Fetch response status:', fetchResponse.status);
        
        if (!fetchResponse.ok) {
          throw new Error(`HTTP error! status: ${fetchResponse.status}`);
        }
        
        const data = await fetchResponse.json();
        console.log('[grantsApi.getGrants] Fetch response data:', data);
        response = { data, status: fetchResponse.status };
      }

      console.log('[grantsApi.getGrants] Response received:', {
        status: response.status,
        dataType: typeof response.data,
        itemsCount: response.data?.items?.length || 0,
        total: response.data?.total || 0,
      });

      // Validate response structure
      if (!response.data || typeof response.data !== 'object') {
        throw new Error('Invalid response format: expected object');
      }

      if (!Array.isArray(response.data.items)) {
        throw new Error('Invalid response format: items should be an array');
      }

      console.log('[grantsApi.getGrants] Returning valid response with', response.data.items.length, 'items');
      return response.data;
    } catch (error) {
      console.error('[grantsApi.getGrants] Error occurred:', error);
      throw error;
    }
  },

  getGrant: async (id: number) => {
    try {
      if (process.env.NODE_ENV === 'development') {
        console.log('[grantsApi.getGrant] Called with id:', id);
      }

      const response = await api.get<Grant>(`${ENDPOINTS.BASE}${id}`);
      
      if (process.env.NODE_ENV === 'development') {
        console.log('[grantsApi.getGrant] Response received:', response.data);
      }

      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('[grantsApi.getGrant] Error occurred:', error);
      }
      throw error;
    }
  },

  createGrant: async (data: CreateGrantInput) => {
    try {
      if (process.env.NODE_ENV === 'development') {
        console.log('[grantsApi.createGrant] Called with data:', data);
      }

      const response = await api.post<Grant>(ENDPOINTS.BASE, data);
      
      if (process.env.NODE_ENV === 'development') {
        console.log('[grantsApi.createGrant] Response received:', response.data);
      }

      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('[grantsApi.createGrant] Error occurred:', error);
      }
      throw error;
    }
  },

  updateGrant: async (id: number, data: Partial<CreateGrantInput>) => {
    try {
      if (process.env.NODE_ENV === 'development') {
        console.log('[grantsApi.updateGrant] Called with id:', id, 'data:', data);
      }

      const response = await api.put<Grant>(`${ENDPOINTS.BASE}${id}`, data);
      
      if (process.env.NODE_ENV === 'development') {
        console.log('[grantsApi.updateGrant] Response received:', response.data);
      }

      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('[grantsApi.updateGrant] Error occurred:', error);
      }
      throw error;
    }
  },

  deleteGrant: async (id: number) => {
    try {
      if (process.env.NODE_ENV === 'development') {
        console.log('[grantsApi.deleteGrant] Called with id:', id);
      }

      await api.delete(`${ENDPOINTS.BASE}${id}`);
      
      if (process.env.NODE_ENV === 'development') {
        console.log('[grantsApi.deleteGrant] Delete successful');
      }
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('[grantsApi.deleteGrant] Error occurred:', error);
      }
      throw error;
    }
  },

  runScraper: async () => {
    try {
      if (process.env.NODE_ENV === 'development') {
        console.log('[grantsApi.runScraper] Called');
      }

      await api.post(ENDPOINTS.SCRAPER_RUN);
      
      if (process.env.NODE_ENV === 'development') {
        console.log('[grantsApi.runScraper] Scraper started successfully');
      }
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('[grantsApi.runScraper] Error occurred:', error);
      }
      throw error;
    }
  },

  getScraperStatus: async (): Promise<ScraperStatus> => {
    try {
      if (process.env.NODE_ENV === 'development') {
        console.log('[grantsApi.getScraperStatus] Called');
      }

      const response = await api.get(ENDPOINTS.SCRAPER_STATUS);
      
      if (process.env.NODE_ENV === 'development') {
        console.log('[grantsApi.getScraperStatus] Response received:', response.data);
      }

      // Transform the array response to match the expected format
      const sources = response.data || [];
      const totalSources = sources.length;
      const successfulSources = sources.filter((s: any) => s.status === 'success').length;
      const errorSources = sources.filter((s: any) => s.status === 'error').length;
      
      return {
        status: totalSources > 0 ? (successfulSources > 0 ? 'active' : 'error') : 'inactive',
        available_sources: sources.map((s: any) => s.source_name),
        active_sources: sources.filter((s: any) => s.status === 'success').map((s: any) => s.source_name),
        last_run: sources.length > 0 ? sources[0].last_run : undefined,
        next_scheduled: sources.length > 0 ? sources[0].next_scheduled : undefined,
        success_count: successfulSources,
        error_count: errorSources
      };
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('[grantsApi.getScraperStatus] Error occurred:', error);
      }
      throw error;
    }
  },

  runScrapers: async (request: ScraperRunRequest) => {
    try {
      if (process.env.NODE_ENV === 'development') {
        console.log('[grantsApi.runScrapers] Called with request:', request);
      }

      const response = await api.post(ENDPOINTS.SCRAPER_RUN, request);
      
      if (process.env.NODE_ENV === 'development') {
        console.log('[grantsApi.runScrapers] Response received:', response.data);
      }

      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('[grantsApi.runScrapers] Error occurred:', error);
      }
      throw error;
    }
  },

  // New endpoints for managing grant sources
  getSources: async () => {
    try {
      if (process.env.NODE_ENV === 'development') {
        console.log('[grantsApi.getSources] Called');
      }

      const response = await api.get<string[]>(ENDPOINTS.SOURCES);
      
      if (process.env.NODE_ENV === 'development') {
        console.log('[grantsApi.getSources] Response received:', response.data);
      }

      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('[grantsApi.getSources] Error occurred:', error);
      }
      throw error;
    }
  },

  getBySource: async (source: string, filters?: GrantFilters) => {
    try {
      if (process.env.NODE_ENV === 'development') {
        console.log('[grantsApi.getBySource] Called with source:', source, 'filters:', filters);
      }

      const response = await api.get<GrantsResponse>(`${ENDPOINTS.BASE}source/${source}`, { 
        params: filters,
        validateStatus: (status) => status < 500,
      });
      
      if (process.env.NODE_ENV === 'development') {
        console.log('[grantsApi.getBySource] Response received:', response.data);
      }

      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('[grantsApi.getBySource] Error occurred:', error);
      }
      throw error;
    }
  },
}; 