'use client';

import { useState } from 'react';
import { useGrants } from '../../../hooks/useGrants';
import { GrantList } from '../../../components/grants/GrantList';
import { GrantForm } from '../../../components/grants/GrantForm';
import { Grant, GrantFilters } from '../../../types/models';
import { Dialog } from '@headlessui/react';

export default function GrantsPage() {
  const [filters, setFilters] = useState<GrantFilters>({
    status: 'open',
    page: 1,
    size: 10,
  });
  const [selectedGrant, setSelectedGrant] = useState<Grant | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);

  const {
    grants,
    total,
    isLoading,
    error,
    runScraper,
    isScraperRunning,
  } = useGrants(filters);

  const handleGrantClick = (grant: Grant) => {
    setSelectedGrant(grant);
    setIsFormOpen(true);
  };

  const handleNewGrant = () => {
    setSelectedGrant(null);
    setIsFormOpen(true);
  };

  const handleStatusChange = (status: 'open' | 'closed' | 'draft' | '') => {
    setFilters((prev) => ({
      ...prev,
      status: status || undefined,
      page: 1,
    }));
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Grants</h1>
          <p className="text-gray-500">
            {total} grant{total !== 1 ? 's' : ''} found
          </p>
        </div>

        <div className="flex space-x-4">
          <button
            onClick={handleNewGrant}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
          >
            Add Grant
          </button>
          <button
            onClick={() => runScraper()}
            disabled={isScraperRunning}
            className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            {isScraperRunning ? 'Running Scraper...' : 'Run Scraper'}
          </button>
        </div>
      </div>

      <div className="mb-6">
        <div className="flex space-x-2">
          <button
            onClick={() => handleStatusChange('')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              !filters.status
                ? 'bg-gray-100 text-gray-900'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            All
          </button>
          <button
            onClick={() => handleStatusChange('open')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filters.status === 'open'
                ? 'bg-gray-100 text-gray-900'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Open
          </button>
          <button
            onClick={() => handleStatusChange('closed')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filters.status === 'closed'
                ? 'bg-gray-100 text-gray-900'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Closed
          </button>
          <button
            onClick={() => handleStatusChange('draft')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filters.status === 'draft'
                ? 'bg-gray-100 text-gray-900'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Draft
          </button>
        </div>
      </div>

      <GrantList filters={filters} onGrantClick={handleGrantClick} />

      <Dialog
        open={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        className="relative z-50"
      >
        <div className="fixed inset-0 bg-black/30" aria-hidden="true" />

        <div className="fixed inset-0 flex items-center justify-center p-4">
          <Dialog.Panel className="mx-auto max-w-2xl w-full bg-white rounded-xl shadow-lg p-6">
            <Dialog.Title className="text-lg font-medium text-gray-900 mb-4">
              {selectedGrant ? 'Edit Grant' : 'New Grant'}
            </Dialog.Title>
            <GrantForm
              grant={selectedGrant || undefined}
              onClose={() => setIsFormOpen(false)}
            />
          </Dialog.Panel>
        </div>
      </Dialog>
    </div>
  );
} 