// Base interfaces for the NavImpact Dashboard

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'user';
  is_active: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface Grant {
  id: number;
  title: string;
  description?: string;
  source: string;
  source_url?: string;
  application_url?: string;
  contact_email?: string;
  min_amount?: number;
  max_amount?: number;
  open_date?: Date;
  deadline?: Date;
  industry_focus?: string;
  location_eligibility?: string;
  org_type_eligible?: string[];
  funding_purpose?: string[];
  audience_tags?: string[];
  status: 'draft' | 'open' | 'closed' | 'archived';
  notes?: string;
  created_at: Date;
  updated_at: Date;
  created_by_id?: number;
  tags?: Tag[];
}

export interface Tag {
  id: string;
  name: string;
  description?: string;
  color?: string;
  grant_count: number;
  project_count: number;
  created_at: Date;
  updated_at: Date;
}

export enum TagCategory {
  INDUSTRY = 'industry',
  LOCATION = 'location',
  ORG_TYPE = 'org_type',
  FUNDING_PURPOSE = 'funding_purpose',
  AUDIENCE = 'audience',
  OTHER = 'other'
}

export interface Task {
  id: string;
  title: string;
  description: string;
  status: 'todo' | 'in_progress' | 'in_review' | 'done' | 'archived';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assignee_id?: string;
  due_date?: Date;
  estimated_hours?: number;
  actual_hours?: number;
  project_id: string;
  creator_id?: string;
  tags: Tag[];
  createdAt: Date;
  updatedAt: Date;
  completed_at?: Date;
}

export interface Project {
  id: string;
  title: string;
  description: string;
  status: 'draft' | 'active' | 'completed' | 'archived';
  owner_id: string;
  start_date: Date;
  end_date?: Date;
  tasks: Task[];
  grants: Grant[];
  tags: Tag[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Comment {
  id: string;
  content: string;
  user_id: string;
  user: User;
  task_id?: string;
  project_id?: string;
  grant_id?: string;
  parent_id?: string;
  replies?: Comment[];
  mentions?: string[];
  reactions?: Record<string, string[]>;
  createdAt: Date;
  updatedAt: Date;
}

export interface TeamMember {
  id: string;
  user_id: string;
  user: User;
  project_id: string;
  role: string;
  joined_at: Date;
}

export interface Metric {
  id: string;
  name: string;
  value: number;
  unit: string;
  category: string;
  project_id?: string;
  grant_id?: string;
  timestamp: Date;
  createdAt: Date;
  updatedAt: Date;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// Form types
export interface CreateGrantRequest {
  title: string;
  description?: string;
  source: string;
  source_url?: string;
  application_url?: string;
  contact_email?: string;
  min_amount?: number;
  max_amount?: number;
  open_date?: Date;
  deadline?: Date;
  industry_focus?: string;
  location_eligibility?: string;
  org_type_eligible?: string[];
  funding_purpose?: string[];
  audience_tags?: string[];
  status: 'draft' | 'open' | 'closed' | 'archived';
  notes?: string;
  tags?: string[];
}

export interface UpdateGrantRequest extends Partial<CreateGrantRequest> {
  id: number;
}

export interface CreateTagRequest {
  name: string;
  color: string;
  category: TagCategory;
  description?: string;
  parent_id?: string;
  synonyms?: string[];
}

export interface UpdateTagRequest extends Partial<CreateTagRequest> {
  id: string;
}

export interface TagFormData {
  name: string;
  description?: string;
  color?: string;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assignee_id?: string;
  due_date?: Date;
  estimated_hours?: number;
  project_id: string;
  tags?: string[];
}

export interface UpdateTaskRequest extends Partial<CreateTaskRequest> {
  id: string;
  status?: 'todo' | 'in_progress' | 'in_review' | 'done' | 'archived';
}

export interface GrantFilters {
  status?: 'draft' | 'open' | 'closed' | 'archived';
  source?: string;
  industry_focus?: string;
  location_eligibility?: string;
  page: number;
  size: number;
}

export interface CreateGrantInput {
  title: string;
  description?: string;
  source: string;
  source_url?: string;
  application_url?: string;
  contact_email?: string;
  min_amount?: number;
  max_amount?: number;
  open_date?: string;
  deadline?: string;
  industry_focus?: string;
  location_eligibility?: string;
  org_type_eligible?: string[];
  funding_purpose?: string[];
  audience_tags?: string[];
  status: 'draft' | 'open' | 'closed' | 'archived';
  notes?: string;
  tags?: string[];
}