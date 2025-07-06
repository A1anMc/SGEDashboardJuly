import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { grantsApi, ScraperRunRequest } from '../services/grants';
import { GrantFilters, Grant, CreateGrantRequest, UpdateGrantRequest } from '../types/models';
import { toast } from 'react-hot-toast';

export const useGrants = (filters: GrantFilters = {}) => {
  const queryClient = useQueryClient();

  // Query for grants list
  const {
    data,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['grants', filters],
    queryFn: () => grantsApi.getGrants(filters),
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });

  // Create grant mutation
  const createMutation = useMutation({
    mutationFn: (grant: CreateGrantRequest) => grantsApi.createGrant(grant),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grants'] });
      queryClient.invalidateQueries({ queryKey: ['grants', 'dashboard'] });
    },
  });

  // Update grant mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, grant }: { id: number; grant: UpdateGrantRequest }) => 
      grantsApi.updateGrant(id, grant),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grants'] });
      queryClient.invalidateQueries({ queryKey: ['grants', 'dashboard'] });
    },
  });

  // Delete grant mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => grantsApi.deleteGrant(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grants'] });
      queryClient.invalidateQueries({ queryKey: ['grants', 'dashboard'] });
    },
  });

  // Run scraper mutation
  const runScraperMutation = useMutation({
    mutationFn: (request?: ScraperRunRequest) => grantsApi.runScrapers(request),
    onSuccess: () => {
      // Refetch grants after a delay to allow scraper to complete
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['grants'] });
        queryClient.invalidateQueries({ queryKey: ['grants', 'dashboard'] });
      }, 5000);
    },
  });

  return {
    grants: data?.items || [],
    total: data?.total || 0,
    page: data?.page || 1,
    size: data?.size || 10,
    hasNext: data?.has_next || false,
    hasPrev: data?.has_prev || false,
    isLoading,
    error,
    refetch,
    createGrant: (grant: CreateGrantRequest) => createMutation.mutate(grant),
    updateGrant: (id: number, grant: UpdateGrantRequest) => 
      updateMutation.mutate({ id, grant }),
    deleteGrant: (id: number) => deleteMutation.mutate(id),
    runScraper: (request?: ScraperRunRequest) => runScraperMutation.mutate(request),
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
    isScraperRunning: runScraperMutation.isPending,
  };
}; 