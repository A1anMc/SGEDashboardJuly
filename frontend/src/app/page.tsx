'use client';

import { FC } from 'react';
import { ChartBarIcon, DocumentTextIcon, TagIcon, ClockIcon } from '@heroicons/react/24/outline';
import { useGrants } from '@/hooks/useGrants';
import { toast } from 'react-hot-toast';

const DashboardPage: FC = () => {
  const { grants, total, isLoading, runScraper, isScraperRunning } = useGrants();

  const stats = [
    { name: 'Total Grants', value: total.toString(), icon: DocumentTextIcon },
    { name: 'Active Tags', value: '45', icon: TagIcon },
    { name: 'Success Rate', value: '24.3%', icon: ChartBarIcon },
    { name: 'Pending Reviews', value: '12', icon: ClockIcon },
  ];

  const handleRunScraper = () => {
    runScraper(undefined, {
      onError: (error) => {
        console.error('Failed to run scraper:', error);
        toast.error('Failed to run scraper');
      },
    });
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div
            key={stat.name}
            className="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6"
          >
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <stat.icon
                  className="h-6 w-6 text-gray-400"
                  aria-hidden="true"
                />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="truncate text-sm font-medium text-gray-500">
                    {stat.name}
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {isLoading ? '...' : stat.value}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Activity */}
        <div className="overflow-hidden rounded-lg bg-white shadow">
          <div className="p-6">
            <h3 className="text-base font-semibold leading-6 text-gray-900">
              Recent Grants
            </h3>
            <div className="mt-6">
              <ul role="list" className="divide-y divide-gray-200">
                {isLoading ? (
                  <li className="py-4">Loading...</li>
                ) : (
                  grants.slice(0, 5).map((grant) => (
                    <li key={grant.id} className="py-4">
                      <div className="flex space-x-3">
                        <div className="flex-1 space-y-1">
                          <h3 className="text-sm font-medium">{grant.title}</h3>
                          <p className="text-sm text-gray-500">
                            {grant.description.slice(0, 100)}...
                          </p>
                        </div>
                        <time className="text-sm text-gray-500">
                          {new Date(grant.created_at).toLocaleDateString()}
                        </time>
                      </div>
                    </li>
                  ))
                )}
              </ul>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="overflow-hidden rounded-lg bg-white shadow">
          <div className="p-6">
            <h3 className="text-base font-semibold leading-6 text-gray-900">
              Quick Actions
            </h3>
            <div className="mt-6 space-y-4">
              <button className="inline-flex w-full items-center justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">
                Add New Grant
              </button>
              <button
                onClick={handleRunScraper}
                disabled={isScraperRunning}
                className="inline-flex w-full items-center justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isScraperRunning ? 'Running Scraper...' : 'Run Scraper'}
              </button>
              <button className="inline-flex w-full items-center justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                Generate Report
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
