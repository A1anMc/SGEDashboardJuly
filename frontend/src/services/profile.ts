import { apiClient } from './api';

export interface UserProfile {
  id: number;
  organisation_name: string;
  organisation_type: string;
  industry_focus?: string;
  location?: string;
  website?: string;
  description?: string;
  preferred_funding_range_min?: number;
  preferred_funding_range_max?: number;
  preferred_industries?: string[];
  preferred_locations?: string[];
  preferred_org_types?: string[];
  max_deadline_days?: number;
  min_grant_amount?: number;
  max_grant_amount?: number;
  email_notifications: string;
  deadline_alerts: number;
  created_at: string;
  updated_at: string;
  user_id?: number;
}

export interface UserProfileCreate {
  organisation_name: string;
  organisation_type: string;
  industry_focus?: string;
  location?: string;
  website?: string;
  description?: string;
  preferred_funding_range_min?: number;
  preferred_funding_range_max?: number;
  preferred_industries?: string[];
  preferred_locations?: string[];
  preferred_org_types?: string[];
  max_deadline_days?: number;
  min_grant_amount?: number;
  max_grant_amount?: number;
  email_notifications: string;
  deadline_alerts: number;
}

export interface UserProfileUpdate {
  organisation_name?: string;
  organisation_type?: string;
  industry_focus?: string;
  location?: string;
  website?: string;
  description?: string;
  preferred_funding_range_min?: number;
  preferred_funding_range_max?: number;
  preferred_industries?: string[];
  preferred_locations?: string[];
  preferred_org_types?: string[];
  max_deadline_days?: number;
  min_grant_amount?: number;
  max_grant_amount?: number;
  email_notifications?: string;
  deadline_alerts?: number;
}

export const profileService = {
  // Get current user's profile
  async getMyProfile(): Promise<UserProfile> {
    return apiClient.request<UserProfile>('/user-profiles/me');
  },

  // Get all user profiles (admin only)
  async getAllProfiles(skip = 0, limit = 100): Promise<UserProfile[]> {
    const queryParams = {
      skip: skip.toString(),
      limit: limit.toString()
    };
    return apiClient.request<UserProfile[]>('/user-profiles/', {}, queryParams);
  },

  // Get specific user profile by ID
  async getProfile(id: number): Promise<UserProfile> {
    return apiClient.request<UserProfile>(`/user-profiles/${id}`);
  },

  // Create new user profile
  async createProfile(profile: UserProfileCreate): Promise<UserProfile> {
    return apiClient.request<UserProfile>('/user-profiles/', {
      method: 'POST',
      body: JSON.stringify(profile),
    });
  },

  // Update current user's profile
  async updateMyProfile(profile: UserProfileUpdate): Promise<UserProfile> {
    return apiClient.request<UserProfile>('/user-profiles/me', {
      method: 'PUT',
      body: JSON.stringify(profile),
    });
  },

  // Update specific user profile by ID
  async updateProfile(id: number, profile: UserProfileUpdate): Promise<UserProfile> {
    return apiClient.request<UserProfile>(`/user-profiles/${id}`, {
      method: 'PUT',
      body: JSON.stringify(profile),
    });
  },

  // Delete user profile
  async deleteProfile(id: number): Promise<{ message: string }> {
    return apiClient.request<{ message: string }>(`/user-profiles/${id}`, {
      method: 'DELETE',
    });
  }
}; 