import { apiClient } from './api';
import { Grant, CreateGrantInput, GrantFilters, PaginatedResponse } from '@/types/models';

// API endpoints
const ENDPOINTS = {
  BASE: '/api/v1/grants/',
  SCRAPER_RUN: '/api/v1/scraper/run',
  SCRAPER_STATUS: '/api/v1/scraper/status',
  SOURCES: '/api/v1/grants/sources',
} as const;

// Grants API service
export const grantsApi = {
  // Get all grants with pagination
  async getGrants(params?: { skip?: number; limit?: number }): Promise<PaginatedResponse<Grant>> {
    try {
      console.log('[grantsApi.getGrants] Fetching grants with params:', params);
      
      const response = await apiClient.getGrants(params);
      
      console.log('[grantsApi.getGrants] Response received:', response);
      
      return response;
    } catch (error) {
      console.error('[grantsApi.getGrants] Error:', error);
      throw error;
    }
  },

  // Get a single grant by ID
  async getGrant(id: string): Promise<Grant> {
    try {
      console.log('[grantsApi.getGrant] Fetching grant:', id);
      
      const response = await apiClient.getGrant(id);
      
      console.log('[grantsApi.getGrant] Response received:', response);
      
      return response;
    } catch (error) {
      console.error('[grantsApi.getGrant] Error:', error);
      throw error;
    }
  },

  // Create a new grant
  async createGrant(grantData: Partial<Grant>): Promise<Grant> {
    try {
      console.log('[grantsApi.createGrant] Creating grant:', grantData);
      
      const response = await apiClient.createGrant(grantData);
      
      console.log('[grantsApi.createGrant] Response received:', response);
      
      return response;
    } catch (error) {
      console.error('[grantsApi.createGrant] Error:', error);
      throw error;
    }
  },

  // Update an existing grant
  async updateGrant(id: string, grantData: Partial<Grant>): Promise<Grant> {
    try {
      console.log('[grantsApi.updateGrant] Updating grant:', id, grantData);
      
      const response = await apiClient.updateGrant(id, grantData);
      
      console.log('[grantsApi.updateGrant] Response received:', response);
      
      return response;
    } catch (error) {
      console.error('[grantsApi.updateGrant] Error:', error);
      throw error;
    }
  },

  // Delete a grant
  async deleteGrant(id: string): Promise<void> {
    try {
      console.log('[grantsApi.deleteGrant] Deleting grant:', id);
      
      await apiClient.deleteGrant(id);
      
      console.log('[grantsApi.deleteGrant] Grant deleted successfully');
    } catch (error) {
      console.error('[grantsApi.deleteGrant] Error:', error);
      throw error;
    }
  },

  // Get grants by source
  async getGrantsBySource(source: string, params?: { skip?: number; limit?: number }): Promise<PaginatedResponse<Grant>> {
    try {
      console.log('[grantsApi.getGrantsBySource] Fetching grants for source:', source, params);
      
      const response = await apiClient.getGrantsBySource(source, params);
      
      console.log('[grantsApi.getGrantsBySource] Response received:', response);
      
      return response;
    } catch (error) {
      console.error('[grantsApi.getGrantsBySource] Error:', error);
      throw error;
    }
  },

  // Run scraper
  async runScraper(): Promise<void> {
    try {
      console.log('[grantsApi.runScraper] Running scraper');
      
      await apiClient.makeRequest(ENDPOINTS.SCRAPER_RUN, { method: 'POST' });
      
      console.log('[grantsApi.runScraper] Scraper started successfully');
    } catch (error) {
      console.error('[grantsApi.runScraper] Error:', error);
      throw error;
    }
  },

  // Get scraper status
  async getScraperStatus(): Promise<any> {
    try {
      console.log('[grantsApi.getScraperStatus] Fetching scraper status');
      
      const response = await apiClient.makeRequest<any>(ENDPOINTS.SCRAPER_STATUS);
      
      console.log('[grantsApi.getScraperStatus] Response received:', response);
      
      return response;
    } catch (error) {
      console.error('[grantsApi.getScraperStatus] Error:', error);
      throw error;
    }
  },

  // Get available sources
  async getSources(): Promise<string[]> {
    try {
      console.log('[grantsApi.getSources] Fetching sources');
      
      const response = await apiClient.makeRequest<string[]>(ENDPOINTS.SOURCES);
      
      console.log('[grantsApi.getSources] Response received:', response);
      
      return response;
    } catch (error) {
      console.error('[grantsApi.getSources] Error:', error);
      throw error;
    }
  },

  // Get grants with filters
  async getGrantsWithFilters(filters: GrantFilters): Promise<PaginatedResponse<Grant>> {
    try {
      console.log('[grantsApi.getGrantsWithFilters] Fetching grants with filters:', filters);
      
      const response = await apiClient.makeRequest<PaginatedResponse<Grant>>(`${ENDPOINTS.BASE}filter`, {
        method: 'POST',
        body: JSON.stringify(filters),
      });
      
      console.log('[grantsApi.getGrantsWithFilters] Response received:', response);
      
      return response;
    } catch (error) {
      console.error('[grantsApi.getGrantsWithFilters] Error:', error);
      throw error;
    }
  },
};

// Export types for use in components
export type { CreateGrantInput, GrantFilters }; 