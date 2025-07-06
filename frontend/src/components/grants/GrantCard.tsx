import React from 'react';
import { Grant } from '../../types/models';
import { format } from 'date-fns';

interface GrantCardProps {
  grant: Grant;
  onClick: (grant: Grant) => void;
}

export function GrantCard({ grant, onClick }: GrantCardProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div
      className="bg-white rounded-lg shadow-sm p-6 cursor-pointer hover:shadow-md transition-shadow"
      onClick={() => onClick(grant)}
    >
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{grant.title}</h3>
        <span
          className={`px-2 py-1 text-xs font-medium rounded-full ${
            grant.status === 'open'
              ? 'bg-green-100 text-green-800'
              : grant.status === 'closed'
              ? 'bg-red-100 text-red-800'
              : 'bg-gray-100 text-gray-800'
          }`}
        >
          {grant.status}
        </span>
      </div>

      <p className="text-gray-600 mb-4 line-clamp-2">{grant.description}</p>

      <div className="flex justify-between items-center mb-4">
        <div className="text-lg font-semibold text-gray-900">
          {formatCurrency(grant.amount)}
        </div>
        {grant.deadline && (
          <div className="text-sm text-gray-500">
            Due: {format(new Date(grant.deadline), 'MMM d, yyyy')}
          </div>
        )}
      </div>

      <div className="flex flex-wrap gap-2">
        {grant.tags.map((tag, index) => (
          <span
            key={index}
            className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full"
          >
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
} 