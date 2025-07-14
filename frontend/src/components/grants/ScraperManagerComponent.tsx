import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { grantsApi, ScraperRunRequest } from '../../services/grants';
import { PlayIcon, ClockIcon, CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import { ErrorAlert } from '../ui/error-alert';
import { ErrorBoundary } from '../ui/error-boundary';
import { handleApiError, getErrorMessage } from '../../utils/error-handling';
import { toast } from 'react-hot-toast';

const ScraperManagerComponent: React.FC = () => {
  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  const [forceRefresh, setForceRefresh] = useState(false);
  const queryClient = useQueryClient();

  // Get scraper status
  const { data: status, isLoading: statusLoading, error: statusError, refetch: refetchStatus } = useQuery({
    queryKey: ['scrapers', 'status'],
    queryFn: grantsApi.getScraperStatus,
    refetchInterval: 10000, // Refetch every 10 seconds
  });

  // Run scrapers mutation
  const runScrapersMutation = useMutation({
    mutationFn: (request: ScraperRunRequest) => grantsApi.runScrapers(request),
    onSuccess: (data) => {
      toast.success(data.message);
      queryClient.invalidateQueries({ queryKey: ['scrapers'] });
      // Clear selections after successful run
      setSelectedSources([]);
      setForceRefresh(false);
    },
    onError: (error) => {
      handleApiError(error, 'Failed to run scrapers');
    },
  });

  const availableSources = status?.available_sources || [];

  const handleSourceToggle = (source: string) => {
    setSelectedSources(prev => 
      prev.includes(source) 
        ? prev.filter(s => s !== source)
        : [...prev, source]
    );
  };

  const handleRunScrapers = () => {
    const request: ScraperRunRequest = {
      sources: selectedSources.length > 0 ? selectedSources : undefined,
      force_refresh: forceRefresh
    };
    runScrapersMutation.mutate(request);
  };

  const getStatusIcon = (currentStatus: string) => {
    switch (currentStatus) {
      case 'running':
        return <ClockIcon className="h-5 w-5 text-yellow-500 animate-spin" />;
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusBadgeColor = (currentStatus: string) => {
    switch (currentStatus) {
      case 'running':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (statusLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (statusError) {
    return (
      <ErrorAlert
        title="Failed to load scraper status"
        message={getErrorMessage(statusError)}
        retryable={true}
        onRetry={() => refetchStatus()}
      />
    );
  }

  return (
    <ErrorBoundary>
      <div className="space-y-4">
        <div className="bg-white shadow rounded-lg p-4">
          <h3 className="text-lg font-medium mb-4">Scraper Status</h3>
          <div className="flex items-center space-x-4">
            <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium ${getStatusBadgeColor(status?.status || 'unknown')}`}>
              {getStatusIcon(status?.status || 'unknown')}
              <span className="ml-2 capitalize">{status?.status || 'Unknown'}</span>
            </div>
            {status?.last_run && (
              <span className="text-sm text-gray-500">
                Last run: {new Date(status.last_run).toLocaleString()}
              </span>
            )}
            {status?.next_scheduled && (
              <span className="text-sm text-gray-500">
                Next run: {new Date(status.next_scheduled).toLocaleString()}
              </span>
            )}
          </div>
          <div className="mt-4 grid grid-cols-2 gap-4">
            <div>
              <span className="text-sm font-medium text-gray-500">Success Count</span>
              <p className="mt-1 text-2xl font-semibold text-green-600">{status?.success_count || 0}</p>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-500">Error Count</span>
              <p className="mt-1 text-2xl font-semibold text-red-600">{status?.error_count || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-4">
          <h3 className="text-lg font-medium mb-4">Available Sources</h3>
          <div className="space-y-2">
            {availableSources.map((source: string) => (
              <label key={source} className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  className="form-checkbox h-5 w-5 text-blue-600"
                  checked={selectedSources.includes(source)}
                  onChange={() => handleSourceToggle(source)}
                  disabled={runScrapersMutation.isPending}
                />
                <span className="text-gray-900">{source}</span>
              </label>
            ))}
          </div>

          <div className="mt-4 space-x-4">
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                className="form-checkbox h-5 w-5 text-blue-600"
                checked={forceRefresh}
                onChange={(e) => setForceRefresh(e.target.checked)}
                disabled={runScrapersMutation.isPending}
              />
              <span className="text-gray-900">Force Refresh</span>
            </label>
          </div>

          <button
            onClick={handleRunScrapers}
            disabled={runScrapersMutation.isPending}
            className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <PlayIcon className="h-5 w-5 mr-2" />
            {runScrapersMutation.isPending ? 'Running...' : 'Run Scrapers'}
          </button>
        </div>
      </div>
    </ErrorBoundary>
  );
};

export default ScraperManagerComponent; 