import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { grantsApi, ScraperRunRequest } from '../../services/grants';
import { toast } from 'react-hot-toast';
import { PlayIcon, ClockIcon, CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

export const ScraperManager: React.FC = () => {
  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  const [forceRefresh, setForceRefresh] = useState(false);
  const queryClient = useQueryClient();

  // Get scraper status
  const { data: status, isLoading: statusLoading } = useQuery({
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
    onError: (error: Error) => {
      toast.error(`Error running scrapers: ${error.message}`);
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

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Grant Scraper Management</h1>
        <p className="text-gray-600">
          Manage automated grant data collection from various sources
        </p>
      </div>

      {/* Current Status */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Current Status</h2>
        </div>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              {getStatusIcon(status?.status || 'idle')}
              <span className="text-lg font-medium text-gray-900">
                {(status?.status || 'idle').charAt(0).toUpperCase() + (status?.status || 'idle').slice(1)}
              </span>
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeColor(status?.status || 'idle')}`}>
                {status?.status || 'idle'}
              </span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
            <div>
              <span className="font-medium">Last Run:</span>{' '}
              {status?.last_run ? new Date(status.last_run).toLocaleString() : 'Never'}
            </div>
            <div>
              <span className="font-medium">Next Scheduled:</span>{' '}
              {status?.next_scheduled ? new Date(status.next_scheduled).toLocaleString() : 'Not scheduled'}
            </div>
          </div>
        </div>
      </div>

      {/* Run Scrapers */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Run Scrapers</h2>
        </div>
        <div className="p-6">
          {/* Source Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Select Sources (leave empty to run all)
            </label>
            <div className="space-y-2">
              {availableSources.map((source) => (
                <label key={source} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={selectedSources.includes(source)}
                    onChange={() => handleSourceToggle(source)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-3 text-sm text-gray-900">{source}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Options */}
          <div className="mb-6">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={forceRefresh}
                onChange={(e) => setForceRefresh(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="ml-3 text-sm text-gray-900">
                Force refresh (re-scrape existing grants)
              </span>
            </label>
          </div>

          {/* Run Button */}
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-500">
              {selectedSources.length > 0 
                ? `Selected: ${selectedSources.join(', ')}`
                : 'All sources will be run'
              }
            </div>
            <button
              onClick={handleRunScrapers}
              disabled={runScrapersMutation.isPending || status?.status === 'running'}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <PlayIcon className="h-4 w-4" />
              <span>
                {runScrapersMutation.isPending ? 'Starting...' : 'Run Scrapers'}
              </span>
            </button>
          </div>

          {/* Info */}
          <div className="mt-4 p-4 bg-blue-50 rounded-md">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-800">
                  About Grant Scraping
                </h3>
                <div className="mt-2 text-sm text-blue-700">
                  <p>
                    Scrapers automatically collect grant information from various government and 
                    institutional websites. This process may take several minutes to complete.
                  </p>
                  <ul className="mt-2 list-disc list-inside space-y-1">
                    <li>New grants are automatically added to the database</li>
                    <li>Existing grants are updated with current information</li>
                    <li>Duplicate detection prevents data redundancy</li>
                    <li>Grant matching scores are calculated automatically</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Available Sources */}
      <div className="mt-6 bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Available Sources</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {availableSources.map((source) => (
              <div key={source} className="border border-gray-200 rounded-lg p-4">
                <h3 className="font-medium text-gray-900">{source}</h3>
                <p className="text-sm text-gray-600 mt-1">
                  {source === 'business.gov.au' && 'Australian Government business grants and programs'}
                  {source === 'grantconnect.gov.au' && 'Government grant opportunity listings'}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};