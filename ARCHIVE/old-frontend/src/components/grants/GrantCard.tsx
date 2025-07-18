import React from 'react';
import { Grant } from '../../types/models';
import { format } from 'date-fns';

interface GrantCardProps {
  grant: Grant;
  onClick: (grant: Grant) => void;
}

export function GrantCard({ grant, onClick }: GrantCardProps) {
  const formatCurrency = (amount: number | undefined) => {
    if (!amount) return 'Amount not specified';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'AUD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDateRange = () => {
    const openDate = grant.open_date ? format(new Date(grant.open_date), 'MMM d, yyyy') : 'Not specified';
    const deadline = grant.deadline ? format(new Date(grant.deadline), 'MMM d, yyyy') : 'Not specified';
    return `${openDate} - ${deadline}`;
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
              : grant.status === 'archived'
              ? 'bg-gray-100 text-gray-500'
              : 'bg-yellow-100 text-yellow-800'
          }`}
        >
          {grant.status}
        </span>
      </div>

      <p className="text-gray-600 mb-4 line-clamp-2">{grant.description}</p>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <div className="text-sm text-gray-500">Amount Range</div>
          <div className="text-sm font-medium">
            {grant.min_amount || grant.max_amount ? (
              <>
                {formatCurrency(grant.min_amount)} - {formatCurrency(grant.max_amount)}
              </>
            ) : (
              'Amount not specified'
            )}
          </div>
        </div>
        <div>
          <div className="text-sm text-gray-500">Source</div>
          <div className="text-sm font-medium">{grant.source}</div>
        </div>
      </div>

      <div className="mb-4">
        <div className="text-sm text-gray-500">Timeline</div>
        <div className="text-sm font-medium">{formatDateRange()}</div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <div className="text-sm text-gray-500">Industry</div>
          <div className="text-sm font-medium">{grant.industry_focus || 'Not specified'}</div>
        </div>
        <div>
          <div className="text-sm text-gray-500">Location</div>
          <div className="text-sm font-medium">{grant.location_eligibility || 'Not specified'}</div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {grant.tags?.map((tag, index) => (
          <span
            key={index}
            className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full"
          >
            {tag.name}
          </span>
        ))}
        {grant.org_type_eligible?.map((type, index) => (
          <span
            key={`org-${index}`}
            className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full"
          >
            {type}
          </span>
        ))}
      </div>
    </div>
  );
} 