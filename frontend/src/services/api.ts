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
    const response = await api.get<Task[]>('/api/tasks');
    return response.data;
  },

  getTask: async (id: string): Promise<Task> => {
    const response = await api.get<Task>(`/api/tasks/${id}`);
    return response.data;
  },

  createTask: async (task: CreateTaskRequest): Promise<Task> => {
    const response = await api.post<Task>('/api/tasks', task);
    return response.data;
  },

  updateTask: async (id: string, task: UpdateTaskRequest): Promise<Task> => {
    const response = await api.put<Task>(`/api/tasks/${id}`, task);
    return response.data;
  },

  deleteTask: async (id: string): Promise<void> => {
    await api.delete(`/api/tasks/${id}`);
  },
};

export const usersApi = {
  getUsers: async (): Promise<User[]> => {
    const response = await api.get<User[]>('/api/users');
    return response.data;
  },

  getUser: async (id: string): Promise<User> => {
    const response = await api.get<User>(`/api/users/${id}`);
    return response.data;
  },
};

export const projectsApi = {
  getProjects: async (): Promise<Project[]> => {
    const response = await api.get<Project[]>('/api/projects');
    return response.data;
  },

  getProject: async (id: string): Promise<Project> => {
    const response = await api.get<Project>(`/api/projects/${id}`);
    return response.data;
  },

  createProject: async (project: Partial<Project>): Promise<Project> => {
    const response = await api.post<Project>('/api/projects', project);
    return response.data;
  },

  updateProject: async (id: string, project: Partial<Project>): Promise<Project> => {
    const response = await api.put<Project>(`/api/projects/${id}`, project);
    return response.data;
  },

  deleteProject: async (id: string): Promise<void> => {
    await api.delete(`/api/projects/${id}`);
  },
};

// Grant APIs moved to grants.ts service file

export const tagsApi = {
  getTags: async (): Promise<Tag[]> => {
    const response = await api.get<Tag[]>('/api/tags');
    return response.data;
  },

  getTag: async (id: string): Promise<Tag> => {
    const response = await api.get<Tag>(`/api/tags/${id}`);
    return response.data;
  },

  createTag: async (tag: CreateTagRequest): Promise<Tag> => {
    const response = await api.post<Tag>('/api/tags', tag);
    return response.data;
  },

  updateTag: async (id: string, tag: UpdateTagRequest): Promise<Tag> => {
    const response = await api.put<Tag>(`/api/tags/${id}`, tag);
    return response.data;
  },

  deleteTag: async (id: string): Promise<void> => {
    await api.delete(`/api/tags/${id}`);
  },
}; 