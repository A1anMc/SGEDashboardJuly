import { config } from '@/lib/config';

export interface UserProfile {
  id: number;
  organization_name: string;
  organization_type: string;
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
  created_at: string;
  updated_at: string;
}

export interface UserProfileCreate {
  organization_name: string;
  organization_type: string;
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

export interface UserProfileUpdate extends Partial<UserProfileCreate> {}

export interface GrantMatch {
  grant_id: number;
  grant_title: string;
  match_score: number;
  match_reasons: string[];
  is_eligible: boolean;
}

class ProfileService {
  private baseUrl = `${config.apiUrl}/api/v1/user-profiles`;

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getProfile(): Promise<{ profile: UserProfile; message: string }> {
    return this.request<{ profile: UserProfile; message: string }>('');
  }

  async createProfile(profileData: UserProfileCreate): Promise<{ profile: UserProfile; message: string }> {
    return this.request<{ profile: UserProfile; message: string }>('', {
      method: 'POST',
      body: JSON.stringify(profileData),
    });
  }

  async updateProfile(profileData: UserProfileUpdate): Promise<{ profile: UserProfile; message: string }> {
    return this.request<{ profile: UserProfile; message: string }>('', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  }

  async getMatchingGrants(): Promise<GrantMatch[]> {
    return this.request<GrantMatch[]>('/matching-grants');
  }

  async seedSampleProfile(): Promise<{ message: string; profile_id: number; organization: string }> {
    return this.request<{ message: string; profile_id: number; organization: string }>('/seed-sample', {
      method: 'POST',
    });
  }

  // Helper method to check if user has a profile
  async hasProfile(): Promise<boolean> {
    try {
      await this.getProfile();
      return true;
    } catch (error) {
      return false;
    }
  }
}

export const profileService = new ProfileService(); 