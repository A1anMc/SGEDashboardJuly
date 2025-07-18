import React from 'react';
import { useMutation } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { grantsApi } from '../../services/grants';
import { useScraperStatus } from '../../hooks/useGrants';

export function ScraperManagerComponent() {
  const { data: scraperStatus, isLoading: statusLoading } = useScraperStatus();

  const runScraperMutation = useMutation({
    mutationFn: () => grantsApi.runScraper(),
    onSuccess: () => {
      toast.success('Scraper started successfully');
    },
    onError: (error) => {
      console.error('Failed to run scraper:', error);
      toast.error('Failed to start scraper. Please try again.');
    },
  });

  const handleRunScraper = () => {
    runScraperMutation.mutate();
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-4">Grant Scraper</h2>
      
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-medium mb-2">Status</h3>
          {statusLoading ? (
            <p className="text-gray-500">Loading status...</p>
          ) : (
            <div className="text-sm">
              <p><strong>Status:</strong> {scraperStatus?.status || 'Unknown'}</p>
              {scraperStatus?.last_run && (
                <p><strong>Last Run:</strong> {new Date(scraperStatus.last_run).toLocaleString()}</p>
              )}
              {scraperStatus?.grants_found && (
                <p><strong>Grants Found:</strong> {scraperStatus.grants_found}</p>
              )}
            </div>
          )}
        </div>

        <div>
          <button
            onClick={handleRunScraper}
            disabled={runScraperMutation.isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {runScraperMutation.isPending ? 'Running...' : 'Run Scraper'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ScraperManagerComponent; 