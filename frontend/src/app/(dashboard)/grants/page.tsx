'use client';

import { useState, useEffect } from 'react';

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

export default function GrantsPage() {
  const [grants, setGrants] = useState<Grant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedGrants, setExpandedGrants] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchGrants();
  }, []);

  const fetchGrants = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('🔍 Testing direct API call...');
      
      // Simple direct API call
      const response = await fetch('https://navimpact-api.onrender.com/api/v1/grants/');
      console.log('📡 Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('✅ API response:', data);

      const grantsData = data?.items || [];
      console.log('📊 Found grants:', grantsData.length);
      setGrants(grantsData);
    } catch (err) {
      console.error('❌ Error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch grants');
    } finally {
      setLoading(false);
    }
  };

  // Helper functions for enhanced grant cards
  const getStatusBadge = (status: string) => {
    const statusConfig = {
      open: { color: 'bg-green-100 text-green-800 border-green-200', text: 'Open' },
      active: { color: 'bg-blue-100 text-blue-800 border-blue-200', text: 'Active' },
      closed: { color: 'bg-red-100 text-red-800 border-red-200', text: 'Closed' },
      draft: { color: 'bg-gray-100 text-gray-800 border-gray-200', text: 'Draft' }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.draft;
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.color}`}>
        {config.text}
      </span>
    );
  };

  const getDeadlineCountdown = (deadline: string) => {
    const now = new Date();
    const deadlineDate = new Date(deadline);
    const diffTime = deadlineDate.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) {
      return { text: 'Expired', color: 'text-red-600', urgency: 'high' };
    } else if (diffDays <= 7) {
      return { text: `${diffDays} days left`, color: 'text-red-600', urgency: 'high' };
    } else if (diffDays <= 30) {
      return { text: `${diffDays} days left`, color: 'text-orange-600', urgency: 'medium' };
    } else {
      return { text: `${diffDays} days left`, color: 'text-green-600', urgency: 'low' };
    }
  };

  const formatAmount = (min?: number, max?: number) => {
    if (!min && !max) return 'Amount not specified';
    if (min && max) {
      return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
    }
    if (min) return `From $${min.toLocaleString()}`;
    if (max) return `Up to $${max.toLocaleString()}`;
    return 'Amount not specified';
  };

  const toggleExpanded = (grantId: string) => {
    const newExpanded = new Set(expandedGrants);
    if (newExpanded.has(grantId)) {
      newExpanded.delete(grantId);
    } else {
      newExpanded.add(grantId);
    }
    setExpandedGrants(newExpanded);
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Grants</h1>
        <p className="text-gray-600">Loading grants...</p>
        <div className="mt-4 bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded">
          <p>🔄 Testing API connection...</p>
        </div>
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
      
      <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6">
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
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {grants.map((grant) => {
            const deadlineInfo = grant.deadline ? getDeadlineCountdown(grant.deadline) : null;
            const isExpanded = expandedGrants.has(grant.id);
            
            return (
              <div key={grant.id} className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
                {/* Header */}
                <div className="p-6 border-b border-gray-100">
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="text-lg font-semibold text-gray-900 line-clamp-2 leading-tight">
                      {grant.title}
                    </h3>
                    <div className="ml-3 flex-shrink-0">
                      {getStatusBadge(grant.status)}
                    </div>
                  </div>
                  
                  {/* Key Info */}
                  <div className="space-y-2">
                    <div className="flex items-center text-sm text-gray-600">
                      <span className="font-medium">Source:</span>
                      <span className="ml-2">{grant.source}</span>
                    </div>
                    
                    <div className="flex items-center text-sm text-gray-600">
                      <span className="font-medium">Funding:</span>
                      <span className="ml-2 font-semibold text-gray-900">
                        {formatAmount(grant.min_amount, grant.max_amount)}
                      </span>
                    </div>
                    
                    {deadlineInfo && (
                      <div className="flex items-center text-sm">
                        <span className="font-medium text-gray-600">Deadline:</span>
                        <span className={`ml-2 font-semibold ${deadlineInfo.color}`}>
                          {deadlineInfo.text}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Description */}
                <div className="p-6">
                  <p className="text-gray-600 text-sm line-clamp-3">
                    {grant.description}
                  </p>
                  
                  {/* Expandable Details */}
                  {isExpanded && (
                    <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
                      {grant.industry_focus && (
                        <div className="flex items-center text-sm">
                          <span className="font-medium text-gray-600 w-20">Industry:</span>
                          <span className="text-gray-900">{grant.industry_focus}</span>
                        </div>
                      )}
                      
                      {grant.location_eligibility && (
                        <div className="flex items-center text-sm">
                          <span className="font-medium text-gray-600 w-20">Location:</span>
                          <span className="text-gray-900">{grant.location_eligibility}</span>
                        </div>
                      )}
                      
                      {grant.org_type_eligible && grant.org_type_eligible.length > 0 && (
                        <div className="flex items-start text-sm">
                          <span className="font-medium text-gray-600 w-20">Eligible:</span>
                          <div className="flex flex-wrap gap-1">
                            {grant.org_type_eligible.map((type, index) => (
                              <span key={index} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                                {type}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                  
                  {/* Action Buttons */}
                  <div className="mt-4 flex items-center justify-between">
                    <button
                      onClick={() => toggleExpanded(grant.id)}
                      className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                    >
                      {isExpanded ? 'Show Less' : 'More Details'}
                    </button>
                    
                    <div className="flex space-x-2">
                      <button className="text-sm text-gray-500 hover:text-gray-700">
                        📌 Save
                      </button>
                      <button className="text-sm text-gray-500 hover:text-gray-700">
                        📧 Contact
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
} 