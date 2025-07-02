import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { grantsApi } from '@/services/grants';
import { GrantFilters, CreateGrantInput, UpdateGrantInput } from '@/types/models';
import { toast } from 'react-hot-toast';

export const useGrants = (filters: GrantFilters = {}) => {
  const queryClient = useQueryClient();

  const {
    data,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['grants', filters],
    queryFn: () => grantsApi.getGrants(filters),
  });

  const createMutation = useMutation({
    mutationFn: grantsApi.createGrant,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grants'] });
      toast.success('Grant created successfully');
    },
    onError: (error: Error) => {
      toast.error(`Error creating grant: ${error.message}`);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, ...data }: UpdateGrantInput) =>
      grantsApi.updateGrant(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grants'] });
      toast.success('Grant updated successfully');
    },
    onError: (error: Error) => {
      toast.error(`Error updating grant: ${error.message}`);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: grantsApi.deleteGrant,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grants'] });
      toast.success('Grant deleted successfully');
    },
    onError: (error: Error) => {
      toast.error(`Error deleting grant: ${error.message}`);
    },
  });

  const runScraperMutation = useMutation({
    mutationFn: grantsApi.runScraper,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grants'] });
      toast.success('Grant scraper completed successfully');
    },
    onError: (error: Error) => {
      toast.error(`Error running scraper: ${error.message}`);
    },
  });

  return {
    grants: data?.items || [],
    total: data?.total || 0,
    isLoading,
    error,
    refetch,
    createGrant: (grant: CreateGrantInput) => createMutation.mutate(grant),
    updateGrant: (grant: UpdateGrantInput) => updateMutation.mutate(grant),
    deleteGrant: (id: number) => deleteMutation.mutate(id),
    runScraper: () => runScraperMutation.mutate(),
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
    isScraperRunning: runScraperMutation.isPending,
  };
}; 