export enum TagCategory {
  INDUSTRY = 'industry',
  LOCATION = 'location',
  ORG_TYPE = 'org_type',
  FUNDING_PURPOSE = 'funding_purpose',
  AUDIENCE = 'audience',
}

export interface Tag {
  id: number;
  name: string;
  category: TagCategory;
  description?: string;
  parents?: Tag[];
  children?: Tag[];
  synonyms?: Tag[];
}

export interface Grant {
  id: number;
  title: string;
  description: string;
  amount: number | null;
  deadline: string | null;
  status: 'open' | 'closed' | 'draft';
  tags: Tag[];
  source_url: string | null;
  source: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateGrantInput {
  title: string;
  description: string;
  amount?: number;
  deadline?: string;
  status: 'open' | 'closed' | 'draft';
  tags: string[];
  source_url?: string;
  source: string;
  notes?: string;
}

export interface UpdateGrantInput extends Partial<CreateGrantInput> {
  id: number;
}

export interface GrantFilters {
  status?: 'open' | 'closed' | 'draft';
  tags?: string[];
  search?: string;
  startDate?: string;
  endDate?: string;
  page?: number;
  size?: number;
}

export interface Project {
  id: number;
  name: string;
  description: string;
  start_date: string;
  end_date: string;
  status: string;
  tags: Tag[];
}

export interface Task {
  id: number;
  title: string;
  description: string;
  due_date: string;
  status: string;
  priority: string;
  assignee_id?: number;
  project_id: number;
  tags: Tag[];
} 