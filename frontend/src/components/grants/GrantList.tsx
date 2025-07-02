import { FC } from 'react';
import { useQuery } from '@tanstack/react-query';
import { grantsApi } from '@/services/grants';
import { Grant, GrantFilters } from '@/types/models';
import { GrantCard } from './GrantCard';

interface GrantListProps {
  filters: GrantFilters;
  onGrantClick: (grant: Grant) => void;
}

export const GrantList: FC<GrantListProps> = ({ filters, onGrantClick }) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['grants', filters],
    queryFn: () => grantsApi.getGrants(filters),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-500">Error loading grants. Please try again.</div>
      </div>
    );
  }

  if (!data?.items.length) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">No grants found.</div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {data.items.map((grant) => (
        <GrantCard
          key={grant.id}
          grant={grant}
          onClick={() => onGrantClick(grant)}
        />
      ))}
    </div>
  );
}; 