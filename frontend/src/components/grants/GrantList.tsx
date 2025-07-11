import { FC } from 'react';
import { useQuery } from '@tanstack/react-query';
import { grantsApi } from '../../services/grants';
import { Grant, GrantFilters } from '../../types/models';
import { GrantCard } from './GrantCard';
import { ErrorAlert } from '../ui/error-alert';
import { ErrorBoundary } from '../ui/error-boundary';
import { getErrorMessage } from '../../utils/error-handling';

interface GrantListProps {
  filters: GrantFilters;
  onGrantClick: (grant: Grant) => void;
}

export const GrantList: FC<GrantListProps> = ({ filters, onGrantClick }) => {
  const { data, isLoading, error, refetch } = useQuery({
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
      <ErrorAlert
        title="Failed to load grants"
        message={getErrorMessage(error)}
        retryable={true}
        onRetry={() => refetch()}
      />
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
    <ErrorBoundary>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.items.map((grant) => (
          <GrantCard
            key={grant.id}
            grant={grant}
            onClick={() => onGrantClick(grant)}
          />
        ))}
      </div>
    </ErrorBoundary>
  );
}; 