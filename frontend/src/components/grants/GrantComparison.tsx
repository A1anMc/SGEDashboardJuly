'use client';

import { useState } from 'react';

interface Grant {
  id: string;
  title: string;
  description: string;
  source: string;
  status: string;
  min_amount?: number;
  max_amount?: number;
  deadline?: string;
  industry_focus?: string;
  location_eligibility?: string;
  org_type_eligible?: string[];
}

interface GrantComparisonProps {
  grants: Grant[];
  onClose: () => void;
}

interface ComparisonMetric {
  label: string;
  value1: string;
  value2: string;
  value3?: string;
  isBetter?: 'grant1' | 'grant2' | 'grant3' | 'equal' | 'depends';
  type: 'text' | 'amount' | 'date' | 'list' | 'status';
}

export default function GrantComparison({ grants, onClose }: GrantComparisonProps) {
  const [selectedGrants, setSelectedGrants] = useState<Grant[]>(grants.slice(0, 3));
  const [showComparison, setShowComparison] = useState(false);

  const formatAmount = (min?: number, max?: number) => {
    if (!min && !max) return 'Not specified';
    if (min && max) {
      return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
    }
    if (min) return `From $${min.toLocaleString()}`;
    if (max) return `Up to $${max.toLocaleString()}`;
    return 'Not specified';
  };

  const formatDeadline = (deadline?: string) => {
    if (!deadline) return 'No deadline';
    const date = new Date(deadline);
    const now = new Date();
    const diffTime = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return 'Expired';
    if (diffDays <= 7) return `${diffDays} days (Urgent)`;
    if (diffDays <= 30) return `${diffDays} days (Soon)`;
    return `${diffDays} days`;
  };

  const getDeadlineUrgency = (deadline?: string) => {
    if (!deadline) return 'low';
    const date = new Date(deadline);
    const now = new Date();
    const diffTime = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return 'expired';
    if (diffDays <= 7) return 'high';
    if (diffDays <= 30) return 'medium';
    return 'low';
  };

  const getAmountRange = (min?: number, max?: number) => {
    if (!min && !max) return 0;
    if (min && max) return (min + max) / 2;
    if (min) return min;
    if (max) return max;
    return 0;
  };

  const generateComparisonMetrics = (): ComparisonMetric[] => {
    if (selectedGrants.length < 2) return [];

    const [grant1, grant2, grant3] = selectedGrants;
    const metrics: ComparisonMetric[] = [];

    // Basic Info
    metrics.push({
      label: 'Title',
      value1: grant1.title,
      value2: grant2.title,
      value3: grant3?.title,
      type: 'text'
    });

    metrics.push({
      label: 'Source',
      value1: grant1.source,
      value2: grant2.source,
      value3: grant3?.source,
      type: 'text'
    });

    metrics.push({
      label: 'Status',
      value1: grant1.status,
      value2: grant2.status,
      value3: grant3?.status,
      type: 'status'
    });

    // Funding Comparison
    const amount1 = getAmountRange(grant1.min_amount, grant1.max_amount);
    const amount2 = getAmountRange(grant2.min_amount, grant2.max_amount);
    const amount3 = grant3 ? getAmountRange(grant3.min_amount, grant3.max_amount) : 0;

    metrics.push({
      label: 'Funding Amount',
      value1: formatAmount(grant1.min_amount, grant1.max_amount),
      value2: formatAmount(grant2.min_amount, grant2.max_amount),
      value3: grant3 ? formatAmount(grant3.min_amount, grant3.max_amount) : '',
      isBetter: amount1 > amount2 ? 'grant1' : amount2 > amount1 ? 'grant2' : 'equal',
      type: 'amount'
    });

    // Deadline Comparison
    const urgency1 = getDeadlineUrgency(grant1.deadline);
    const urgency2 = getDeadlineUrgency(grant2.deadline);
    const urgency3 = grant3 ? getDeadlineUrgency(grant3.deadline) : 'low';

    metrics.push({
      label: 'Deadline',
      value1: formatDeadline(grant1.deadline),
      value2: formatDeadline(grant2.deadline),
      value3: grant3 ? formatDeadline(grant3.deadline) : '',
      isBetter: urgency1 === 'high' ? 'grant1' : urgency2 === 'high' ? 'grant2' : 'equal',
      type: 'date'
    });

    // Industry
    metrics.push({
      label: 'Industry Focus',
      value1: grant1.industry_focus || 'Not specified',
      value2: grant2.industry_focus || 'Not specified',
      value3: grant3?.industry_focus || 'Not specified',
      type: 'text'
    });

    // Location
    metrics.push({
      label: 'Location Eligibility',
      value1: grant1.location_eligibility || 'Not specified',
      value2: grant2.location_eligibility || 'Not specified',
      value3: grant3?.location_eligibility || 'Not specified',
      type: 'text'
    });

    // Organization Types
    metrics.push({
      label: 'Eligible Organizations',
      value1: grant1.org_type_eligible?.join(', ') || 'Not specified',
      value2: grant2.org_type_eligible?.join(', ') || 'Not specified',
      value3: grant3?.org_type_eligible?.join(', ') || 'Not specified',
      type: 'list'
    });

    return metrics;
  };

  const getComparisonClass = (isBetter: string | undefined, index: number) => {
    if (!isBetter) return '';
    
    const grantIndex = index + 1;
    if (isBetter === `grant${grantIndex}`) return 'bg-green-50 border-green-200';
    if (isBetter === 'equal') return 'bg-blue-50 border-blue-200';
    return 'bg-gray-50 border-gray-200';
  };

  const getComparisonIcon = (isBetter: string | undefined, index: number) => {
    if (!isBetter) return null;
    
    const grantIndex = index + 1;
    if (isBetter === `grant${grantIndex}`) return '🏆';
    if (isBetter === 'equal') return '⚖️';
    return null;
  };

  const handleGrantSelection = (grant: Grant, index: number) => {
    const newSelected = [...selectedGrants];
    newSelected[index] = grant;
    setSelectedGrants(newSelected);
  };

  const comparisonMetrics = generateComparisonMetrics();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-7xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Grant Comparison Tool</h2>
            <p className="text-gray-600 mt-1">Compare grants side-by-side to make informed decisions</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Grant Selection */}
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Grants to Compare</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[0, 1, 2].map((index) => (
              <div key={index} className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  Grant {index + 1}
                </label>
                <select
                  value={selectedGrants[index]?.id || ''}
                  onChange={(e) => {
                    const selectedGrant = grants.find(g => g.id === e.target.value);
                    if (selectedGrant) {
                      handleGrantSelection(selectedGrant, index);
                    }
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select a grant...</option>
                  {grants.map((grant) => (
                    <option key={grant.id} value={grant.id}>
                      {grant.title}
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </div>
          
          <div className="mt-4 flex justify-end">
            <button
              onClick={() => setShowComparison(true)}
              disabled={selectedGrants.filter(Boolean).length < 2}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              Compare Grants
            </button>
          </div>
        </div>

        {/* Comparison Results */}
        {showComparison && comparisonMetrics.length > 0 && (
          <div className="flex-1 overflow-y-auto p-6 max-h-[60vh]">
            <div className="space-y-6">
              {comparisonMetrics.map((metric, index) => (
                <div key={index} className="border border-gray-200 rounded-lg overflow-hidden">
                  <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                    <h4 className="font-medium text-gray-900">{metric.label}</h4>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 divide-x divide-gray-200">
                    {[0, 1, 2].map((grantIndex) => {
                      const value = grantIndex === 0 ? metric.value1 : 
                                   grantIndex === 1 ? metric.value2 : metric.value3;
                      const isBetter = metric.isBetter;
                      const comparisonClass = getComparisonClass(isBetter, grantIndex);
                      const icon = getComparisonIcon(isBetter, grantIndex);
                      
                      return (
                        <div
                          key={grantIndex}
                          className={`p-4 ${comparisonClass} ${grantIndex === 2 ? '' : 'md:border-r'}`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <p className="text-sm text-gray-900 font-medium">
                                {value || 'Not available'}
                              </p>
                            </div>
                            {icon && (
                              <span className="ml-2 text-lg" title="Best option">
                                {icon}
                              </span>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>

            {/* Summary */}
            <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-blue-900 mb-3">Comparison Summary</h3>
              <div className="space-y-2 text-sm text-blue-800">
                <p>• <strong>Funding:</strong> Higher amounts are generally better for larger projects</p>
                <p>• <strong>Deadline:</strong> Urgent deadlines require immediate action</p>
                <p>• <strong>Eligibility:</strong> Check if your organization type matches</p>
                <p>• <strong>Location:</strong> Ensure you meet geographic requirements</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 