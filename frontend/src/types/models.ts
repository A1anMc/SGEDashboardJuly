// Base interfaces for the SGE Dashboard

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
  createdAt: Date;
  updatedAt: Date;
}

export interface Grant {
  id: string;
  title: string;
  description: string;
  amount: number;
  deadline: Date;
  status: 'open' | 'closed' | 'draft';
  tags: Tag[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Tag {
  id: string;
  name: string;
  category: TagCategory;
  description?: string;
  parent_id?: number;
  synonyms?: string[];
  created_by_id?: number;
  createdAt: Date;
  updatedAt: Date;
  grant_count?: number;
  project_count?: number;
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
  assignedTo?: string;
  dueDate?: Date;
  tags?: Tag[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'completed' | 'on_hold';
  startDate: Date;
  endDate?: Date;
  tasks: Task[];
  grants: Grant[];
  tags: Tag[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Comment {
  id: string;
  content: string;
  authorId: string;
  author: User;
  taskId?: string;
  projectId?: string;
  grantId?: string;
  parentId?: string;
  replies?: Comment[];
  createdAt: Date;
  updatedAt: Date;
}

export interface TeamMember {
  id: string;
  userId: string;
  user: User;
  role: string;
  permissions: string[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Metric {
  id: string;
  name: string;
  value: number;
  unit: string;
  category: string;
  projectId?: string;
  grantId?: string;
  recordedAt: Date;
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
  description: string;
  amount: number;
  deadline: Date;
  tags: string[];
}

export interface UpdateGrantRequest extends Partial<CreateGrantRequest> {
  id: string;
}

export interface CreateTagRequest {
  name: string;
  category: TagCategory;
  description?: string;
  parent_id?: number;
  synonyms?: string[];
}

export interface UpdateTagRequest extends Partial<CreateTagRequest> {
  id: string;
}

export interface CreateTaskRequest {
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  assignedTo?: string;
  dueDate?: Date;
  tags: string[];
}

export interface UpdateTaskRequest extends Partial<CreateTaskRequest> {
  id: string;
  status?: 'todo' | 'in_progress' | 'in_review' | 'done' | 'archived';
}

export interface GrantFilters {
  status?: 'open' | 'closed' | 'draft';
  tags?: string[];
  search?: string;
  minAmount?: number;
  maxAmount?: number;
  deadlineAfter?: Date;
  deadlineBefore?: Date;
  page?: number;
  size?: number;
}