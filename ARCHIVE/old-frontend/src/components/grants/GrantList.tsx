import { FC } from 'react';
import { Grant } from '../../types/models';
import { GrantCard } from './GrantCard';
import { ErrorAlert } from '../ui/error-alert';
import { ErrorBoundary } from '../ui/error-boundary';
import { getErrorMessage } from '../../utils/error-handling';
import React from 'react';

interface GrantListProps {
  grants: Grant[];
  isLoading: boolean;
  error: any;
  onGrantClick: (grant: Grant) => void;
  onRetry?: () => void;
}

export const GrantList: FC<GrantListProps> = ({ 
  grants, 
  isLoading, 
  error, 
  onGrantClick, 
  onRetry 
}) => {
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
        onRetry={onRetry}
      />
    );
  }

  if (!grants.length) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">No grants found.</div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {grants.map((grant) => (
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