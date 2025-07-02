export interface Grant {
  id: number;
  title: string;
  description: string;
  amount: number | null;
  deadline: string | null;
  status: 'open' | 'closed' | 'draft';
  tags: string[];
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