import { apiClient } from './api';

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateUserRequest {
  email: string;
  full_name: string;
  password: string;
}

export interface UpdateUserRequest {
  email?: string;
  full_name?: string;
  is_active?: boolean;
}

export const usersService = {
  // Get all users
  async getAllUsers(skip = 0, limit = 100): Promise<User[]> {
    return apiClient.getUsers({ skip, limit });
  },

  // Get user by ID
  async getUserById(id: string): Promise<User> {
    return apiClient.getUser(id);
  },

  // Get current user
  async getCurrentUser(): Promise<User> {
    return apiClient.getCurrentUser();
  },

  // Create new user
  async createUser(userData: CreateUserRequest): Promise<User> {
    return apiClient.makeRequest<User>(`/api/v1/users/`, {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  // Update user
  async updateUser(id: string, userData: UpdateUserRequest): Promise<User> {
    return apiClient.makeRequest<User>(`/api/v1/users/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  },

  // Delete user
  async deleteUser(id: string): Promise<{ message: string }> {
    return apiClient.makeRequest<{ message: string }>(`/api/v1/users/${id}/`, {
      method: 'DELETE',
    });
  }
}; 