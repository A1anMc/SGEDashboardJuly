import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { grantsApi, ScraperRunRequest } from '../services/grants';
import { GrantFilters, Grant, CreateGrantRequest, UpdateGrantRequest, CreateGrantInput } from '../types/models';
import { toast } from 'react-hot-toast';

export const useGrants = (filters: GrantFilters = { page: 1, size: 10 }) => {
  const queryClient = useQueryClient();

  // Query for grants list with retry and error handling
  const {
    data,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['grants', filters],
    queryFn: () => grantsApi.getGrants(filters),
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
    retry: 3, // Retry failed requests 3 times
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000)
  });

  // Create grant mutation with improved error handling
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
      queryClient.invalidateQueries({ queryKey: ['grants', 'dashboard'] });
      toast.success('Grant created successfully');
    },
    onError: (error) => {
      console.error('Failed to create grant:', error);
      toast.error('Failed to create grant. Please try again.');
    },
  });

  // Update grant mutation with improved error handling
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
      queryClient.invalidateQueries({ queryKey: ['grants', 'dashboard'] });
      toast.success('Grant updated successfully');
    },
    onError: (error) => {
      console.error('Failed to update grant:', error);
      toast.error('Failed to update grant. Please try again.');
    },
  });

  // Delete grant mutation with improved error handling
  const deleteMutation = useMutation({
    mutationFn: (id: string) => grantsApi.deleteGrant(Number(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grants'] });
      queryClient.invalidateQueries({ queryKey: ['grants', 'dashboard'] });
      toast.success('Grant deleted successfully');
    },
    onError: (error) => {
      console.error('Failed to delete grant:', error);
      toast.error('Failed to delete grant. Please try again.');
    },
  });

  // Run scraper mutation with improved error handling
  const runScraperMutation = useMutation({
    mutationFn: (request?: ScraperRunRequest) => {
      const scraperRequest: ScraperRunRequest = request || {};
      return grantsApi.runScrapers(scraperRequest);
    },
    onSuccess: () => {
      toast.success('Scraper started successfully');
      // Refetch grants after a delay to allow scraper to complete
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['grants'] });
        queryClient.invalidateQueries({ queryKey: ['grants', 'dashboard'] });
      }, 5000);
    },
    onError: (error) => {
      console.error('Failed to run scraper:', error);
      toast.error('Failed to start scraper. Please try again.');
    },
  });

  return {
    grants: data?.items || [],
    total: data?.total || 0,
    page: data?.page || 1,
    size: data?.size || 10,
    hasNext: data ? (data.page * data.size) < data.total : false,
    hasPrev: data ? data.page > 1 : false,
    isLoading,
    error,
    refetch,
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
}; 