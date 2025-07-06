import axios from 'axios';

const baseURL = process.env.BACKEND_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for cookies/auth
});

// Add request interceptor for auth
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage or cookie if needed
    const token = localStorage.getItem('token');
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
  async (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API service instances
export const tasksApi = {
  getAll: () => api.get('/api/v1/tasks'),
  getById: (id: string) => api.get(`/api/v1/tasks/${id}`),
  create: (data: any) => api.post('/api/v1/tasks', data),
  update: (id: string, data: any) => api.put(`/api/v1/tasks/${id}`, data),
  delete: (id: string) => api.delete(`/api/v1/tasks/${id}`),
};

export const usersApi = {
  getAll: () => api.get('/api/v1/users'),
  getById: (id: string) => api.get(`/api/v1/users/${id}`),
  create: (data: any) => api.post('/api/v1/users', data),
  update: (id: string, data: any) => api.put(`/api/v1/users/${id}`, data),
  delete: (id: string) => api.delete(`/api/v1/users/${id}`),
};

export const projectsApi = {
  getAll: () => api.get('/api/v1/projects'),
  getById: (id: string) => api.get(`/api/v1/projects/${id}`),
  create: (data: any) => api.post('/api/v1/projects', data),
  update: (id: string, data: any) => api.put(`/api/v1/projects/${id}`, data),
  delete: (id: string) => api.delete(`/api/v1/projects/${id}`),
};

// Export the main api instance
export { api };
export default api; 