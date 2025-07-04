import { FC } from 'react';
import { Grant } from '@/types/models';

interface GrantCardProps {
  grant: Grant;
  onClick: () => void;
}

export const GrantCard: FC<GrantCardProps> = ({ grant, onClick }) => {
  const statusColors = {
    open: 'bg-green-100 text-green-800',
    closed: 'bg-red-100 text-red-800',
    draft: 'bg-gray-100 text-gray-800',
  };

  return (
    <div
      className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 cursor-pointer"
      onClick={onClick}
    >
      <div className="p-4">
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
            {grant.title}
          </h3>
          <span
            className={`px-2 py-1 text-xs font-medium rounded-full ${
              statusColors[grant.status]
            }`}
          >
            {grant.status}
          </span>
        </div>

        <p className="text-gray-600 text-sm mb-4 line-clamp-3">
          {grant.description}
        </p>

        <div className="flex flex-wrap gap-2 mb-4">
          {grant.tags.map((tag) => (
            <span
              key={tag.id}
              className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full"
            >
              {tag.name}
            </span>
          ))}
        </div>

        <div className="flex justify-between items-center text-sm text-gray-500">
          <div className="flex items-center">
            <span className="font-medium">
              {grant.amount ? `$${grant.amount.toLocaleString()}` : 'Amount TBD'}
            </span>
          </div>
          {grant.deadline && (
            <div>
              <span>Due: {new Date(grant.deadline).toLocaleDateString()}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}; 