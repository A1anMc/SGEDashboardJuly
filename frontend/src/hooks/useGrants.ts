import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { grantsApi, CreateGrantInput, GrantFilters } from '../services/grants';
import { Grant, PaginatedResponse } from '@/types/models';

// Query keys
export const grantKeys = {
  all: ['grants'] as const,
  lists: () => [...grantKeys.all, 'list'] as const,
  list: (filters: GrantFilters) => [...grantKeys.lists(), filters] as const,
  details: () => [...grantKeys.all, 'detail'] as const,
  detail: (id: string) => [...grantKeys.details(), id] as const,
  sources: () => [...grantKeys.all, 'sources'] as const,
  scraperStatus: () => [...grantKeys.all, 'scraper-status'] as const,
};

// Hook for fetching grants with filters
export const useGrants = (filters: GrantFilters) => {
  return useQuery({
    queryKey: grantKeys.list(filters),
    queryFn: async () => {
      const result = await grantsApi.getGrantsWithFilters(filters);
      return result;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook for fetching all grants with pagination
export const useGrantsList = (params?: { skip?: number; limit?: number }) => {
  return useQuery({
    queryKey: [...grantKeys.lists(), params],
    queryFn: async () => {
      const result = await grantsApi.getGrants(params);
      return result;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook for fetching a single grant
export const useGrant = (id: string) => {
  return useQuery({
    queryKey: grantKeys.detail(id),
    queryFn: async () => {
      const result = await grantsApi.getGrant(id);
      return result;
    },
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook for creating a grant
export const useCreateGrant = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (grantInput: CreateGrantInput) => {
      // Convert string dates to Date objects and string tags to Tag objects
      const grantData = {
        ...grantInput,
        open_date: grantInput.open_date ? new Date(grantInput.open_date) : undefined,
        deadline: grantInput.deadline ? new Date(grantInput.deadline) : undefined,
        tags: grantInput.tags?.map(tagName => ({ name: tagName } as any)) || undefined,
      };
      return grantsApi.createGrant(grantData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: grantKeys.lists() });
    },
  });
};

// Hook for updating a grant
export const useUpdateGrant = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, grantInput }: { id: string; grantInput: CreateGrantInput }) => {
      // Convert string dates to Date objects and string tags to Tag objects
      const grantData = {
        ...grantInput,
        open_date: grantInput.open_date ? new Date(grantInput.open_date) : undefined,
        deadline: grantInput.deadline ? new Date(grantInput.deadline) : undefined,
        tags: grantInput.tags?.map(tagName => ({ name: tagName } as any)) || undefined,
      };
      return grantsApi.updateGrant(id, grantData);
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: grantKeys.lists() });
      queryClient.invalidateQueries({ queryKey: grantKeys.detail(id) });
    },
  });
};

// Hook for deleting a grant
export const useDeleteGrant = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      return grantsApi.deleteGrant(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: grantKeys.lists() });
    },
  });
};

// Hook for running scraper
export const useRunScraper = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      return grantsApi.runScraper();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: grantKeys.lists() });
      queryClient.invalidateQueries({ queryKey: grantKeys.scraperStatus() });
    },
  });
};

// Hook for getting scraper status
export const useScraperStatus = () => {
  return useQuery({
    queryKey: grantKeys.scraperStatus(),
    queryFn: async () => {
      return grantsApi.getScraperStatus();
    },
    refetchInterval: 5000, // Poll every 5 seconds
    staleTime: 0, // Always consider stale
  });
};

// Hook for getting sources
export const useSources = () => {
  return useQuery({
    queryKey: grantKeys.sources(),
    queryFn: async () => {
      return grantsApi.getSources();
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

// Hook for getting grants by source
export const useGrantsBySource = (source: string, params?: { skip?: number; limit?: number }) => {
  return useQuery({
    queryKey: [...grantKeys.lists(), 'source', source, params],
    queryFn: async () => {
      return grantsApi.getGrantsBySource(source, params);
    },
    enabled: !!source,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}; 