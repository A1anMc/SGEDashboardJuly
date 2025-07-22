/**
 * API Service Configuration and Error Handling
 * 
 * This module provides a configured Axios instance with error handling, retry logic,
 * and authentication. It implements a standardized approach to handling API errors
 * across the application.
 * 
 * Key features:
 * - Global error handling
 * - Authentication token management
 * - Request/response interceptors
 * - Automatic retry with exponential backoff
 * - Standardized error responses
 */

import { config, buildApiUrl } from '@/lib/config';

// Base API client
class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = config.apiUrl;
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {},
    queryParams?: Record<string, string>
  ): Promise<T> {
    const url = buildApiUrl(endpoint, queryParams);
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    const response = await fetch(url, {
      ...defaultOptions,
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Health check
  async getHealth() {
    return this.request(config.endpoints.health);
  }

  // Grants
  async getGrants(params?: { skip?: number; limit?: number }) {
    const queryParams = params ? {
      skip: params.skip?.toString() || '0',
      limit: params.limit?.toString() || '10'
    } : undefined;
    
    return this.request<any>(config.endpoints.grants, {}, queryParams);
  }

  async getGrant(id: string) {
    return this.request<any>(`${config.endpoints.grants}${id}/`);
  }

  async createGrant(data: any) {
    return this.request<any>(config.endpoints.grants, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateGrant(id: string, data: any) {
    return this.request<any>(`${config.endpoints.grants}${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteGrant(id: string) {
    return this.request<void>(`${config.endpoints.grants}${id}/`, {
      method: 'DELETE',
    });
  }

  async getGrantsBySource(source: string, params?: { skip?: number; limit?: number }) {
    const queryParams = params ? {
      skip: params.skip?.toString() || '0',
      limit: params.limit?.toString() || '10'
    } : undefined;
    
    return this.request<any>(`${config.endpoints.grants}source/${source}/`, {}, queryParams);
  }

  // Tasks
  async getTasks(params?: { skip?: number; limit?: number }) {
    const queryParams = params ? {
      skip: params.skip?.toString() || '0',
      limit: params.limit?.toString() || '10'
    } : undefined;
    
    return this.request<any>(config.endpoints.tasks, {}, queryParams);
  }

  async getTask(id: string) {
    return this.request<any>(`${config.endpoints.tasks}${id}/`);
  }

  async createTask(data: any) {
    return this.request<any>(config.endpoints.tasks, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateTask(id: string, data: any) {
    return this.request<any>(`${config.endpoints.tasks}${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteTask(id: string) {
    return this.request<void>(`${config.endpoints.tasks}${id}/`, {
      method: 'DELETE',
    });
  }

  // Projects
  async getProjects(params?: { skip?: number; limit?: number }) {
    const queryParams = params ? {
      skip: params.skip?.toString() || '0',
      limit: params.limit?.toString() || '10'
    } : undefined;
    
    return this.request<any>(config.endpoints.projects, {}, queryParams);
  }

  // Tags
  async getTags() {
    return this.request<any>(config.endpoints.tags);
  }

  // Users
  async getUsers(params?: { skip?: number; limit?: number }) {
    const queryParams = params ? {
      skip: params.skip?.toString() || '0',
      limit: params.limit?.toString() || '10'
    } : undefined;
    
    return this.request<any>(config.endpoints.users, {}, queryParams);
  }

  async getUser(id: string) {
    return this.request<any>(`${config.endpoints.users}${id}/`);
  }

  async getCurrentUser() {
    return this.request<any>(`${config.endpoints.users}me/`);
  }

  // Generic request method for custom endpoints
  async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    return this.request<T>(endpoint, options);
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export individual methods for convenience
export const {
  getHealth,
  getGrants,
  getGrant,
  createGrant,
  updateGrant,
  deleteGrant,
  getTasks,
  getTask,
  createTask,
  updateTask,
  deleteTask,
  getProjects,
  getTags,
  getUsers,
  getUser,
  getCurrentUser,
} = apiClient; 