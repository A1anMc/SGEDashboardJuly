export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      grants: {
        Row: {
          id: number
          title: string
          description: string | null
          source: string
          source_url: string | null
          application_url: string | null
          contact_email: string | null
          min_amount: number | null
          max_amount: number | null
          open_date: string | null
          deadline: string | null
          industry_focus: string | null
          location_eligibility: string | null
          org_type_eligible: string[] | null
          funding_purpose: string[] | null
          audience_tags: string[] | null
          status: 'draft' | 'open' | 'closed' | 'archived'
          notes: string | null
          created_at: string
          updated_at: string
          created_by_id: number | null
        }
        Insert: {
          id?: number
          title: string
          description?: string | null
          source: string
          source_url?: string | null
          application_url?: string | null
          contact_email?: string | null
          min_amount?: number | null
          max_amount?: number | null
          open_date?: string | null
          deadline?: string | null
          industry_focus?: string | null
          location_eligibility?: string | null
          org_type_eligible?: string[] | null
          funding_purpose?: string[] | null
          audience_tags?: string[] | null
          status: 'draft' | 'open' | 'closed' | 'archived'
          notes?: string | null
          created_at?: string
          updated_at?: string
          created_by_id?: number | null
        }
        Update: {
          id?: number
          title?: string
          description?: string | null
          source?: string
          source_url?: string | null
          application_url?: string | null
          contact_email?: string | null
          min_amount?: number | null
          max_amount?: number | null
          open_date?: string | null
          deadline?: string | null
          industry_focus?: string | null
          location_eligibility?: string | null
          org_type_eligible?: string[] | null
          funding_purpose?: string[] | null
          audience_tags?: string[] | null
          status?: 'draft' | 'open' | 'closed' | 'archived'
          notes?: string | null
          created_at?: string
          updated_at?: string
          created_by_id?: number | null
        }
      }
      // Add other tables as needed
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
  }
} 