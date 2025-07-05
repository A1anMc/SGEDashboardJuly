// Base interfaces for the SGE Dashboard

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
  id: number; // Changed from string to number
  title: string;
  description: string;
  source: string;
  
  // Matching criteria
  industry_focus: 'media' | 'creative_arts' | 'technology' | 'general';
  location_eligibility: 'Australia' | 'VIC' | 'NSW' | 'QLD' | 'SA' | 'WA' | 'TAS' | 'NT' | 'ACT';
  org_type_eligible: string[];
  funding_purpose: string[];
  audience_tags: string[];
  
  // Timing and amount
  open_date: Date;
  deadline: Date;
  min_amount?: number;
  max_amount?: number;
  
  // Status and metadata
  status: 'active' | 'closed' | 'draft';
  created_at: Date; // Changed from createdAt
  updated_at: Date; // Changed from updatedAt
  
  // Additional data
  application_url?: string;
  contact_email?: string;
  notes?: string;
  
  // Computed fields
  match_score?: number;
  matched_criteria?: string[];
  missing_criteria?: string[];
}

export interface Tag {
  id: number; // Changed from string to number
  name: string;
  color?: string; // Made optional since backend doesn't have this
  category: TagCategory;
  description?: string;
  parent_id?: number; // Changed from string to number
  synonyms?: string[];
  created_at: Date; // Changed from createdAt
  updated_at: Date; // Changed from updatedAt
  
  // Usage counts for admin
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
  id: number; // Changed from string to number
  title: string;
  description: string;
  status: 'draft' | 'active' | 'completed' | 'archived';
  owner_id: number; // Changed from string to number
  start_date: Date;
  end_date?: Date;
  tasks: Task[];
  grants: Grant[];
  tags: Tag[];
  created_at: Date; // Changed from createdAt
  updated_at: Date; // Changed from updatedAt
  
  // Project profile for grant matching
  location?: string;
  org_type?: string;
  funding_purposes?: string[];
  themes?: string[];
  timeline?: {
    start: string;
    end?: string;
  };
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
  id: number; // Changed from string to number
  name: string;
  value: number;
  unit: string;
  category: string;
  project_id?: number; // Changed from string to number
  grant_id?: number; // Changed from string to number
  timestamp: Date;
  created_at: Date; // Changed from createdAt
  updated_at: Date; // Changed from updatedAt
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
  source: string;
  industry_focus: Grant['industry_focus'];
  location_eligibility: Grant['location_eligibility'];
  org_type_eligible: string[];
  funding_purpose: string[];
  audience_tags: string[];
  open_date: Date;
  deadline: Date;
  min_amount?: number;
  max_amount?: number;
  application_url?: string;
  contact_email?: string;
  notes?: string;
}

export interface UpdateGrantRequest extends Partial<CreateGrantRequest> {
  id: number; // Changed from string to number
  status?: Grant['status'];
}

export interface CreateTagRequest {
  name: string;
  category: TagCategory;
  description?: string;
  parent_id?: number; // Changed from string to number
  synonyms?: string[];
}

export interface UpdateTagRequest extends Partial<CreateTagRequest> {
  id: number; // Changed from string to number
}

export interface CreateTaskRequest {
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assignee_id?: string;
  due_date?: Date;
  estimated_hours?: number;
  project_id: string;
  tags: string[];
}

export interface UpdateTaskRequest extends Partial<CreateTaskRequest> {
  id: string;
  status?: 'todo' | 'in_progress' | 'in_review' | 'done' | 'archived';
}

// Grant dashboard types
export interface GrantDashboard {
  metrics: {
    total_active: number;
    total_amount_available: number;
    upcoming_deadlines: number;
    avg_match_score: number;
  };
  categories: {
    by_industry: Record<string, number>;
    by_location: Record<string, number>;
    by_org_type: Record<string, number>;
    by_funding_range: Record<string, number>;
  };
  timeline: {
    this_week: DeadlineGroup;
    next_week: DeadlineGroup;
    this_month: DeadlineGroup;
    next_month: DeadlineGroup;
    later: DeadlineGroup;
  };
  matching_insights: {
    best_matches: Array<{
      grant_id: number;
      title: string;
      score: number;
    }>;
    common_mismatches: string[];
    suggested_improvements: string[];
  };
  last_updated: Date;
}

export interface DeadlineGroup {
  grants: Array<{
    id: number;
    title: string;
    deadline: Date;
    amount?: number;
  }>;
  total_amount: number;
  count: number;
}

// Grant filters
export interface GrantFilters {
  industry_focus?: string;
  location_eligibility?: string;
  status?: string;
  min_amount?: number;
  max_amount?: number;
  deadline_before?: Date;
  deadline_after?: Date;
  search?: string;
  page?: number;
  size?: number;
}

// Grant matching
export interface GrantMatchResult {
  grant_id: number;
  score: number;
  matched_criteria: string[];
  missing_criteria: string[];
  grant_title: string;
  deadline: Date;
  max_amount?: number;
}

export interface ProjectProfile {
  location: string;
  org_type: string;
  funding_purposes: string[];
  themes: string[];
  timeline: {
    start: string;
    end?: string;
  };
}