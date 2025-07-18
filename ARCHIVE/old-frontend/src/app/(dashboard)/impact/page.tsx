'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../../services/api';

interface ImpactMetrics {
  total_projects: number;
  total_grants: number;
  total_funding: number;
  impact_score: number;
}

interface ImpactData {
  message: string;
  metrics: ImpactMetrics;
}

export default function ImpactPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['impact'],
    queryFn: async () => {
      const response = await api.get<ImpactData>('/impact/');
      return response.data;
    },
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
        <div className="text-red-500">Failed to load impact metrics</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Impact Dashboard</h1>
        <p className="text-gray-500">Track your organization's impact and progress</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900">Total Projects</h3>
          <p className="text-3xl font-bold text-blue-600">{data?.metrics.total_projects || 0}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900">Total Grants</h3>
          <p className="text-3xl font-bold text-green-600">{data?.metrics.total_grants || 0}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900">Total Funding</h3>
          <p className="text-3xl font-bold text-purple-600">${data?.metrics.total_funding || 0}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900">Impact Score</h3>
          <p className="text-3xl font-bold text-orange-600">{data?.metrics.impact_score || 0}</p>
        </div>
      </div>

      <div className="mt-8 bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Impact Overview</h2>
        <p className="text-gray-600">
          This dashboard provides an overview of your organization's impact metrics. 
          Track your progress across projects, grants, and funding to measure your success.
        </p>
      </div>
    </div>
  );
} 