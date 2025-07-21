'use client';

import { useState, useEffect } from 'react';
import { getGrants } from '@/services/api';

interface Grant {
  id: string;
  title: string;
  description: string;
  source: string;
  status: string;
  min_amount?: number;
  max_amount?: number;
  deadline?: string;
}

export default function GrantsPage() {
  const [grants, setGrants] = useState<Grant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchGrants();
  }, []);

  const fetchGrants = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getGrants({ skip: 0, limit: 50 });
      console.log('Grants response:', response);

      const grantsData = (response as any)?.items || [];
      setGrants(grantsData);
    } catch (err) {
      console.error('Error fetching grants:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch grants');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Grants</h1>
        <p className="text-gray-600">Loading grants...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Grants</h1>
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>Error: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-4">Grants</h1>
      <p className="text-gray-600 mb-6">Browse available funding opportunities</p>
      
      <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
        <p>✅ API integration working! Found {grants.length} grants.</p>
        <p className="mt-2 text-sm">
          API Status: <a href="https://navimpact-api.onrender.com/api/v1/grants/" target="_blank" className="underline">Check API</a>
        </p>
      </div>
      
      {grants.length === 0 ? (
        <div className="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded">
          <p>No grants found. Add some sample grants to get started!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {grants.map((grant) => (
            <div key={grant.id} className="border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-900">{grant.title}</h3>
              <p className="text-gray-600 mt-1">{grant.description}</p>
              <div className="mt-2 text-sm text-gray-500">
                <span>Source: {grant.source}</span>
                {grant.min_amount && grant.max_amount && (
                  <span className="ml-4">
                    Amount: ${grant.min_amount.toLocaleString()} - ${grant.max_amount.toLocaleString()}
                  </span>
                )}
                {grant.deadline && (
                  <span className="ml-4">
                    Deadline: {new Date(grant.deadline).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
} 