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

import axios from 'axios';
import { handleApiError, shouldRetry, getRetryDelay } from '../utils/error-handling';
import { 
  ApiResponse, 
  Task, 
  User, 
  Project, 
  CreateTaskRequest, 
  UpdateTaskRequest
} from '../types/models';

// Define missing request types locally
interface CreateUserRequest {
  email: string;
  full_name: string;
  role: 'admin' | 'user';
}

interface UpdateUserRequest extends Partial<CreateUserRequest> {
  id: string;
}

interface CreateProjectRequest {
  title: string;
  description: string;
  owner_id: string;
  start_date: Date;
  end_date?: Date;
}

interface UpdateProjectRequest extends Partial<CreateProjectRequest> {
  id: string;
}

// Get the API URL from environment variables with a production fallback
const baseURL = process.env.NEXT_PUBLIC_API_URL || (
  process.env.NODE_ENV === 'production' 
    ? 'https://sge-dashboard-api.onrender.com'
    : 'http://localhost:8000'
);

// Ensure we have the correct API version path
const normalizedBaseURL = baseURL.includes('/api/v1') 
  ? baseURL 
  : `${baseURL}/api/v1`;

/**
 * Configured Axios instance for API requests
 * - Includes authentication header management
 * - Handles CORS with credentials
 * - Implements global error handling
 * - Provides automatic retry for failed requests
 */
const api = axios.create({
  baseURL: normalizedBaseURL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: false, // Disable for CORS compatibility
  timeout: 10000, // Reduce to 10 second timeout
});

/**
 * Request interceptor for authentication
 * - Adds authentication token to requests if available
 * - Token is retrieved from localStorage
 * - Handles request errors
 */
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage or cookie if needed
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Log request in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config);
    }
    
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

/**
 * Response interceptor for error handling
 * - Implements retry logic for failed requests
 * - Handles authentication errors
 * - Processes and standardizes error responses
 * 
 * Retry Strategy:
 * - Retries on network errors and 5xx responses
 * - Uses exponential backoff with jitter
 * - Maximum 3 retry attempts
 * 
 * Error Handling:
 * - 401: Redirects to login
 * - Other errors: Processed by handleApiError
 */
api.interceptors.response.use(
  (response) => {
    // Log response in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data);
    }
    return response;
  },
  async (error) => {
    const config = error.config;

    // Log error details in development
    if (process.env.NODE_ENV === 'development') {
      console.error('[API Error]', {
        url: config?.url,
        method: config?.method,
        status: error.response?.status,
        data: error.response?.data,
        error: error.message
      });
    }

    // Check if we should retry the request
    if (!config._retry && shouldRetry(error, config._retryCount || 0)) {
      config._retry = true;
      config._retryCount = (config._retryCount || 0) + 1;

      // Wait for the calculated delay
      const delay = getRetryDelay(config._retryCount);
      await new Promise(resolve => setTimeout(resolve, delay));

      // Retry the request
      return api(config);
    }

    // Handle unauthorized access
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    // Handle other errors
    handleApiError(error);
    return Promise.reject(error);
  }
);

/**
 * Task-related API endpoints
 * @typedef {Object} Task
 * @property {string} id - Task ID
 * @property {string} title - Task title
 * @property {string} description - Task description
 */
export const tasksApi = {
  getAll: () => api.get<ApiResponse<Task[]>>('/tasks/'),
  getById: (id: string) => api.get<ApiResponse<Task>>(`/tasks/${id}/`),
  create: (data: CreateTaskRequest) => api.post<ApiResponse<Task>>('/tasks/', data),
  update: (id: string, data: UpdateTaskRequest) => api.put<ApiResponse<Task>>(`/tasks/${id}/`, data),
  delete: (id: string) => api.delete<ApiResponse<void>>(`/tasks/${id}/`),
};

/**
 * User-related API endpoints
 * @typedef {Object} User
 * @property {string} id - User ID
 * @property {string} email - User email
 */
export const usersApi = {
  getAll: () => api.get<ApiResponse<User[]>>('/users/'),
  getById: (id: string) => api.get<ApiResponse<User>>(`/users/${id}/`),
  create: (data: CreateUserRequest) => api.post<ApiResponse<User>>('/users/', data),
  update: (id: string, data: UpdateUserRequest) => api.put<ApiResponse<User>>(`/users/${id}/`, data),
  delete: (id: string) => api.delete<ApiResponse<void>>(`/users/${id}/`),
};

/**
 * Project-related API endpoints
 * @typedef {Object} Project
 * @property {string} id - Project ID
 * @property {string} name - Project name
 */
export const projectsApi = {
  getAll: () => api.get<ApiResponse<Project[]>>('/projects/'),
  getById: (id: string) => api.get<ApiResponse<Project>>(`/projects/${id}/`),
  create: (data: CreateProjectRequest) => api.post<ApiResponse<Project>>('/projects/', data),
  update: (id: string, data: UpdateProjectRequest) => api.put<ApiResponse<Project>>(`/projects/${id}/`, data),
  delete: (id: string) => api.delete<ApiResponse<void>>(`/projects/${id}/`),
};

// Export the main api instance
export { api };
export default api; 