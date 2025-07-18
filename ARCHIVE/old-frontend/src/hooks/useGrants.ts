import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { grantsApi, ScraperRunRequest } from '../services/grants';
import { GrantFilters, Grant, CreateGrantRequest, UpdateGrantRequest, CreateGrantInput } from '../types/models';
import { toast } from 'react-hot-toast';

export const useGrants = (filters: GrantFilters = { page: 1, size: 10 }) => {
  const queryClient = useQueryClient();

  console.log('[useGrants] Hook called with filters:', filters);

  // Simplified query implementation
  const queryResult = useQuery({
    queryKey: ['grants', filters],
    queryFn: async () => {
      console.log('[useGrants] Query function called');
      
      try {
        const result = await grantsApi.getGrants(filters);
        console.log('[useGrants] Query function success:', result);
        return result;
      } catch (error) {
        console.error('[useGrants] Query function error:', error);
        throw error;
      }
    },
    enabled: true,
    staleTime: 0,
    retry: 1,
    refetchOnWindowFocus: false,
    refetchOnMount: true,
  });

  console.log('[useGrants] Query result:', {
    data: queryResult.data,
    isLoading: queryResult.isLoading,
    isFetching: queryResult.isFetching,
    isError: queryResult.isError,
    error: queryResult.error,
  });

  // Create grant mutation
  const createMutation = useMutation({
    mutationFn: (grant: CreateGrantRequest) => {
      const grantInput: CreateGrantInput = {
        ...grant,
        deadline: grant.deadline?.toISOString(),
        open_date: grant.open_date?.toISOString(),
        status: grant.status,
        tags: grant.tags || [],
      };
      return grantsApi.createGrant(grantInput);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grants'] });
      toast.success('Grant created successfully');
    },
    onError: (error) => {
      console.error('Failed to create grant:', error);
      toast.error('Failed to create grant. Please try again.');
    },
  });

  // Update grant mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, grant }: { id: string; grant: UpdateGrantRequest }) => {
      const grantInput: CreateGrantInput = {
        title: grant.title || '',
        description: grant.description || '',
        source: grant.source || '',
        source_url: grant.source_url,
        application_url: grant.application_url,
        contact_email: grant.contact_email,
        min_amount: grant.min_amount,
        max_amount: grant.max_amount,
        open_date: grant.open_date?.toISOString(),
        deadline: grant.deadline?.toISOString(),
        industry_focus: grant.industry_focus,
        location_eligibility: grant.location_eligibility,
        org_type_eligible: grant.org_type_eligible,
        funding_purpose: grant.funding_purpose,
        audience_tags: grant.audience_tags,
        status: grant.status || 'draft',
        notes: grant.notes,
        tags: grant.tags || [],
      };
      return grantsApi.updateGrant(Number(id), grantInput);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grants'] });
      toast.success('Grant updated successfully');
    },
    onError: (error) => {
      console.error('Failed to update grant:', error);
      toast.error('Failed to update grant. Please try again.');
    },
  });

  // Delete grant mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => grantsApi.deleteGrant(Number(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grants'] });
      toast.success('Grant deleted successfully');
    },
    onError: (error) => {
      console.error('Failed to delete grant:', error);
      toast.error('Failed to delete grant. Please try again.');
    },
  });

  // Run scraper mutation
  const runScraperMutation = useMutation({
    mutationFn: (request?: ScraperRunRequest) => {
      const scraperRequest: ScraperRunRequest = request || {};
      return grantsApi.runScrapers(scraperRequest);
    },
    onSuccess: () => {
      toast.success('Scraper started successfully');
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['grants'] });
      }, 5000);
    },
    onError: (error) => {
      console.error('Failed to run scraper:', error);
      toast.error('Failed to start scraper. Please try again.');
    },
  });

  const result = {
    grants: queryResult.data?.items || [],
    total: queryResult.data?.total || 0,
    page: queryResult.data?.page || 1,
    size: queryResult.data?.size || 10,
    hasNext: queryResult.data ? (queryResult.data.page * queryResult.data.size) < queryResult.data.total : false,
    hasPrev: queryResult.data ? queryResult.data.page > 1 : false,
    isLoading: queryResult.isLoading,
    isFetching: queryResult.isFetching,
    isError: queryResult.isError,
    error: queryResult.error,
    refetch: queryResult.refetch,
    createGrant: (grant: CreateGrantRequest) => createMutation.mutate(grant),
    updateGrant: (id: string, grant: UpdateGrantRequest) => 
      updateMutation.mutate({ id, grant }),
    deleteGrant: (id: string) => deleteMutation.mutate(id),
    runScraper: (request?: ScraperRunRequest) => runScraperMutation.mutate(request),
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
    isScraperRunning: runScraperMutation.isPending,
  };

  console.log('[useGrants] Returning result:', {
    grantsCount: result.grants.length,
    total: result.total,
    isLoading: result.isLoading,
    isError: result.isError,
  });

  return result;
}; 