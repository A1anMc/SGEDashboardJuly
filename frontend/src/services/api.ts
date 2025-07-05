import axios, { AxiosError, AxiosResponse } from 'axios';
import { Task, User, Project, Grant, Tag, CreateTaskRequest, UpdateTaskRequest, CreateGrantRequest, UpdateGrantRequest, CreateTagRequest, UpdateTagRequest } from '@/types/models';

const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage or your auth state management
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized errors
    if (error.response?.status === 401) {
      // Clear invalid token
      localStorage.removeItem('auth_token');
      
      // Redirect to login page or handle refresh token logic
      window.location.href = '/login';
      return Promise.reject(error);
    }

    // Handle specific error cases with custom messages
    if (error.response) {
      // Server responded with non-2xx status
      const errorMessage = error.response.data?.message || 'An error occurred';
      console.error('API Error:', {
        status: error.response.status,
        message: errorMessage,
        data: error.response.data
      });
    } else if (error.request) {
      // Request made but no response received
      console.error('Network Error: No response received', error.request);
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }

    return Promise.reject(error);
  }
);

// API response type
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

// Error response type
export interface ApiError {
  message: string;
  status: number;
  errors?: Record<string, string[]>;
}

// Type-safe API methods
export const tasksApi = {
  getTasks: async (): Promise<Task[]> => {
    const response = await api.get<Task[]>('/api/v1/tasks');
    return response.data;
  },

  getTask: async (id: string): Promise<Task> => {
    const response = await api.get<Task>(`/api/v1/tasks/${id}`);
    return response.data;
  },

  createTask: async (task: CreateTaskRequest): Promise<Task> => {
    const response = await api.post<Task>('/api/v1/tasks', task);
    return response.data;
  },

  updateTask: async (id: string, task: UpdateTaskRequest): Promise<Task> => {
    const response = await api.put<Task>(`/api/v1/tasks/${id}`, task);
    return response.data;
  },

  deleteTask: async (id: string): Promise<void> => {
    await api.delete(`/api/v1/tasks/${id}`);
  },
};

export const usersApi = {
  getUsers: async (): Promise<User[]> => {
    const response = await api.get<User[]>('/api/v1/users');
    return response.data;
  },

  getUser: async (id: string): Promise<User> => {
    const response = await api.get<User>(`/api/v1/users/${id}`);
    return response.data;
  },
};

export const projectsApi = {
  getProjects: async (): Promise<Project[]> => {
    const response = await api.get<Project[]>('/api/v1/projects');
    return response.data;
  },

  getProject: async (id: string): Promise<Project> => {
    const response = await api.get<Project>(`/api/v1/projects/${id}`);
    return response.data;
  },

  createProject: async (project: Partial<Project>): Promise<Project> => {
    const response = await api.post<Project>('/api/v1/projects', project);
    return response.data;
  },

  updateProject: async (id: string, project: Partial<Project>): Promise<Project> => {
    const response = await api.put<Project>(`/api/v1/projects/${id}`, project);
    return response.data;
  },

  deleteProject: async (id: string): Promise<void> => {
    await api.delete(`/api/v1/projects/${id}`);
  },
};

export const grantsApi = {
  getGrants: async (): Promise<Grant[]> => {
    const response = await api.get<Grant[]>('/api/v1/grants');
    return response.data;
  },

  getGrant: async (id: string): Promise<Grant> => {
    const response = await api.get<Grant>(`/api/v1/grants/${id}`);
    return response.data;
  },

  createGrant: async (grant: CreateGrantRequest): Promise<Grant> => {
    const response = await api.post<Grant>('/api/v1/grants', grant);
    return response.data;
  },

  updateGrant: async (id: string, grant: UpdateGrantRequest): Promise<Grant> => {
    const response = await api.put<Grant>(`/api/v1/grants/${id}`, grant);
    return response.data;
  },

  deleteGrant: async (id: string): Promise<void> => {
    await api.delete(`/api/v1/grants/${id}`);
  },
};

export const tagsApi = {
  getTags: async (): Promise<Tag[]> => {
    const response = await api.get<Tag[]>('/api/v1/tags');
    return response.data;
  },

  getTag: async (id: string): Promise<Tag> => {
    const response = await api.get<Tag>(`/api/v1/tags/${id}`);
    return response.data;
  },

  createTag: async (tag: CreateTagRequest): Promise<Tag> => {
    const response = await api.post<Tag>('/api/v1/tags', tag);
    return response.data;
  },

  updateTag: async (id: string, tag: UpdateTagRequest): Promise<Tag> => {
    const response = await api.put<Tag>(`/api/v1/tags/${id}`, tag);
    return response.data;
  },

  deleteTag: async (id: string): Promise<void> => {
    await api.delete(`/api/v1/tags/${id}`);
  },
}; 