import { apiClient } from './api';
import { Tag, CreateTagRequest, UpdateTagRequest } from '@/types/models';

// Tags API service
export const tagsApi = {
  // Get all tags
  async getTags(): Promise<Tag[]> {
    try {
      const response = await apiClient.getTags();
      return response;
    } catch (error) {
      console.error('[tagsApi.getTags] Error:', error);
      throw error;
    }
  },

  // Create a new tag
  async createTag(tagData: CreateTagRequest): Promise<Tag> {
    try {
      const response = await apiClient.makeRequest<Tag>('/api/v1/tags/', {
        method: 'POST',
        body: JSON.stringify(tagData),
      });
      return response;
    } catch (error) {
      console.error('[tagsApi.createTag] Error:', error);
      throw error;
    }
  },

  // Update an existing tag
  async updateTag(id: string, tagData: UpdateTagRequest): Promise<Tag> {
    try {
      const response = await apiClient.makeRequest<Tag>(`/api/v1/tags/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(tagData),
      });
      return response;
    } catch (error) {
      console.error('[tagsApi.updateTag] Error:', error);
      throw error;
    }
  },

  // Delete a tag
  async deleteTag(id: string): Promise<void> {
    try {
      await apiClient.makeRequest(`/api/v1/tags/${id}/`, {
        method: 'DELETE',
      });
    } catch (error) {
      console.error('[tagsApi.deleteTag] Error:', error);
      throw error;
    }
  },
}; 