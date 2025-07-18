import { api } from './api';
import { Tag, TagFormData, TagCategory } from '../types/models';

export interface TagsResponse {
  items: Tag[];
  total: number;
  page: number;
  size: number;
}

export interface TagFilters {
  category?: TagCategory;
  search?: string;
  page?: number;
  size?: number;
}

export const tagsApi = {
  getTags: async (filters?: TagFilters) => {
    const params = new URLSearchParams();
    if (filters?.category) params.append('category', filters.category);
    if (filters?.search) params.append('search', filters.search);
    if (filters?.page) params.append('page', filters.page.toString());
    if (filters?.size) params.append('size', filters.size.toString());
    
    const response = await api.get<TagsResponse>(`/tags/?${params.toString()}`);
    return response.data;
  },
  
  getTag: async (id: number) => {
    const response = await api.get<Tag>(`/tags/${id}/`);
    return response.data;
  },
  
  createTag: async (data: TagFormData) => {
    const response = await api.post<Tag>('/tags/', data);
    return response.data;
  },
  
  updateTag: async (id: number, data: Partial<TagFormData>) => {
    const response = await api.put<Tag>(`/tags/${id}/`, data);
    return response.data;
  },
  
  deleteTag: async (id: number) => {
    await api.delete(`/tags/${id}/`);
  },
  
  getTagsByCategory: async (category: TagCategory) => {
    const response = await api.get<Tag[]>(`/tags/category/${category}/`);
    return response.data;
  },
  
  searchTags: async (query: string, category?: TagCategory) => {
    const params = new URLSearchParams({ q: query });
    if (category) params.append('category', category);
    
    const response = await api.get<Tag[]>(`/tags/search/?${params.toString()}`);
    return response.data;
  },
  
  validateTagName: async (name: string, excludeId?: number) => {
    const params = new URLSearchParams({ name });
    if (excludeId) params.append('exclude_id', excludeId.toString());
    
    const response = await api.get<boolean>(`/tags/validate/${name}/?${params.toString()}`);
    return response.data;
  }
}; 