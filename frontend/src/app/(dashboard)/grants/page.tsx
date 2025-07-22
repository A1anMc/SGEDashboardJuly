'use client';

import { useState, useEffect } from 'react';
import GrantComparison from '@/components/grants/GrantComparison';
import PersonalizedGrantsDashboard from '@/components/grants/PersonalizedGrantsDashboard';

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

interface Filters {
  search: string;
  deadline: string;
  minAmount: number;
  maxAmount: number;
  industry: string;
  location: string;
  orgType: string;
  status: string;
}

export default function GrantsPage() {
  const [activeTab, setActiveTab] = useState<'all' | 'personalized'>('personalized');
  const [grants, setGrants] = useState<Grant[]>([]);
  const [filteredGrants, setFilteredGrants] = useState<Grant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedGrants, setExpandedGrants] = useState<Set<string>>(new Set());
  const [showFilters, setShowFilters] = useState(false);
  const [showComparison, setShowComparison] = useState(false);
  
  // Filter state
  const [filters, setFilters] = useState<Filters>({
    search: '',
    deadline: '',
    minAmount: 0,
    maxAmount: 1000000,
    industry: '',
    location: '',
    orgType: '',
    status: ''
  });

  useEffect(() => {
    fetchGrants();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [grants, filters]);

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

  const applyFilters = () => {
    let filtered = [...grants];

    // Search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(grant =>
        grant.title.toLowerCase().includes(searchLower) ||
        grant.description.toLowerCase().includes(searchLower) ||
        grant.source.toLowerCase().includes(searchLower)
      );
    }

    // Deadline filter
    if (filters.deadline) {
      const now = new Date();
      filtered = filtered.filter(grant => {
        if (!grant.deadline) return false;
        const deadline = new Date(grant.deadline);
        
        switch (filters.deadline) {
          case 'closing-soon':
            const daysDiff = Math.ceil((deadline.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
            return daysDiff <= 7 && daysDiff >= 0;
          case 'this-month':
            return deadline.getMonth() === now.getMonth() && deadline.getFullYear() === now.getFullYear();
          case 'next-3-months':
            const threeMonthsFromNow = new Date(now.getFullYear(), now.getMonth() + 3, now.getDate());
            return deadline <= threeMonthsFromNow;
          default:
            return true;
        }
      });
    }

    // Amount filter
    filtered = filtered.filter(grant => {
      const grantMin = grant.min_amount || 0;
      const grantMax = grant.max_amount || 0;
      return grantMin >= filters.minAmount && (grantMax === 0 || grantMax <= filters.maxAmount);
    });

    // Industry filter
    if (filters.industry) {
      filtered = filtered.filter(grant => grant.industry_focus === filters.industry);
    }

    // Location filter
    if (filters.location) {
      filtered = filtered.filter(grant => grant.location_eligibility === filters.location);
    }

    // Organisation type filter
    if (filters.orgType) {
      filtered = filtered.filter(grant => 
        grant.org_type_eligible?.includes(filters.orgType)
      );
    }

    // Status filter
    if (filters.status) {
      filtered = filtered.filter(grant => grant.status === filters.status);
    }

    setFilteredGrants(filtered);
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      deadline: '',
      minAmount: 0,
      maxAmount: 1000000,
      industry: '',
      location: '',
      orgType: '',
      status: ''
    });
  };

  const updateFilter = (key: keyof Filters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
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

  // New micro-insights functions
  const getQuickSummary = (grant: Grant) => {
    const summaries = {
      'Digital Media Innovation Fund': {
        who: 'Digital media startups and creative tech companies',
        why: 'Supports innovative digital storytelling and audience engagement',
        key: 'Focus on technology-driven creative projects'
      },
      'Indigenous Film Production Grant': {
        who: 'Indigenous filmmakers and cultural organisations',
        why: 'Preserves cultural heritage through authentic storytelling',
        key: 'Priority for Indigenous-owned companies'
      },
      'Youth Mental Health Initiative': {
        who: 'Community health organisations and nonprofits',
        why: 'Addresses critical youth mental health challenges',
        key: 'Evidence-based programs preferred'
      },
      'Social Enterprise Accelerator': {
        who: 'Social enterprises and impact-driven nonprofits',
        why: 'Scales social impact through sustainable business models',
        key: 'Must have proven social impact model'
      },
      'Renewable Energy Innovation Grant': {
        who: 'Energy startups and research institutions',
        why: 'Accelerates Australia\'s clean energy transition',
        key: 'Must demonstrate commercial potential'
      },
      'Circular Economy Solutions': {
        who: 'Manufacturers and sustainability innovators',
        why: 'Reduces waste through circular business models',
        key: 'Focus on scalable circular economy solutions'
      },
      'Sustainable Agriculture Innovation': {
        who: 'Farmers and agricultural researchers',
        why: 'Promotes environmentally sustainable farming practices',
        key: 'Must demonstrate environmental benefits'
      },
      'Marine Conservation Initiative': {
        who: 'Marine biologists and conservation organisations',
        why: 'Protects Australia\'s unique marine ecosystems',
        key: 'Priority for Great Barrier Reef projects'
      }
    };

    return summaries[grant.title as keyof typeof summaries] || {
              who: 'Organisations in relevant sectors',
      why: 'Supports important initiatives in this field',
      key: 'Check eligibility requirements carefully'
    };
  };

  const getSectorRelevance = (grant: Grant) => {
    const sectorGroups = {
      'technology': ['Digital Media Innovation Fund', 'Renewable Energy Innovation Grant'],
      'healthcare': ['Youth Mental Health Initiative'],
      'services': ['Indigenous Film Production Grant', 'Social Enterprise Accelerator'],
      'environment': ['Circular Economy Solutions', 'Marine Conservation Initiative'],
      'agriculture': ['Sustainable Agriculture Innovation']
    };

    const sector = grant.industry_focus;
    if (!sector || !sectorGroups[sector as keyof typeof sectorGroups]) {
      return null;
    }

    const similarGrants = sectorGroups[sector as keyof typeof sectorGroups].filter(
      title => title !== grant.title
    );

    if (similarGrants.length === 0) return null;

    const count = similarGrants.length;
    const sectorName = sector.charAt(0).toUpperCase() + sector.slice(1);
    
    return {
      text: `Similar to ${count} other ${sector} grant${count > 1 ? 's' : ''}`,
      count: count,
      sector: sectorName
    };
  };

  const getUrgencyBadge = (deadline?: string) => {
    if (!deadline) return null;
    
    const now = new Date();
    const deadlineDate = new Date(deadline);
    const diffTime = deadlineDate.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) {
      return { text: 'Expired', color: 'bg-red-100 text-red-800 border-red-200', icon: '⏰' };
    } else if (diffDays <= 7) {
      return { text: `Closing in ${diffDays} days!`, color: 'bg-red-100 text-red-800 border-red-200', icon: '🚨' };
    } else if (diffDays <= 14) {
      return { text: `Closing in ${diffDays} days`, color: 'bg-orange-100 text-orange-800 border-orange-200', icon: '⚠️' };
    } else if (diffDays <= 30) {
      return { text: `Closing in ${diffDays} days`, color: 'bg-yellow-100 text-yellow-800 border-yellow-200', icon: '⏳' };
    }
    
    return null;
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

  const exportToCSV = () => {
    if (filteredGrants.length === 0) {
      alert('No grants to export. Please adjust your filters or add some grants.');
      return;
    }

    // Prepare CSV data
    const headers = [
      'Title',
      'Description', 
      'Source',
      'Min Amount',
      'Max Amount',
      'Deadline',
      'Status',
      'Industry Focus',
      'Location Eligibility',
              'Organisation Types Eligible'
    ];

    const csvData = filteredGrants.map(grant => [
      grant.title || '',
      grant.description || '',
      grant.source || '',
      grant.min_amount || '',
      grant.max_amount || '',
      grant.deadline ? new Date(grant.deadline).toLocaleDateString() : '',
      grant.status || '',
      grant.industry_focus || '',
      grant.location_eligibility || '',
      grant.org_type_eligible ? grant.org_type_eligible.join('; ') : ''
    ]);

    // Create CSV content
    const csvContent = [headers, ...csvData]
      .map(row => row.map(cell => `"${cell}"`).join(','))
      .join('\n');

    // Create and trigger download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    
    // Generate filename with current date
    const now = new Date();
    const dateStr = now.toISOString().split('T')[0]; // YYYY-MM-DD format
    const filename = `navimpact-grants-export-${dateStr}.csv`;
    
    link.download = filename;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Cleanup
    window.URL.revokeObjectURL(url);
    
    // Show success message
    alert(`✅ Exported ${filteredGrants.length} grants to ${filename}`);
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
    <div className="container mx-auto p-4 sm:p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Grants</h1>
          <p className="text-sm sm:text-base text-gray-600">Browse available funding opportunities</p>
        </div>
        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
          <button
            onClick={() => setShowComparison(true)}
            className="bg-purple-600 text-white px-4 py-3 sm:py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center justify-center text-sm sm:text-base"
            title="Compare grants side-by-side"
          >
            ⚖️ Compare
          </button>
          <button
            onClick={exportToCSV}
            className="bg-green-600 text-white px-4 py-3 sm:py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center text-sm sm:text-base"
            title="Export filtered grants to CSV"
          >
            📊 Export CSV
          </button>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="bg-blue-600 text-white px-4 py-3 sm:py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm sm:text-base"
          >
            {showFilters ? 'Hide Filters' : 'Show Filters'}
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('personalized')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'personalized'
                  ? 'border-energy-coral text-energy-coral'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              🎯 Personalized Matches
            </button>
            <button
              onClick={() => setActiveTab('all')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'all'
                  ? 'border-energy-coral text-energy-coral'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📋 All Grants
            </button>
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'personalized' ? (
        <PersonalizedGrantsDashboard limit={12} showFilters={true} />
      ) : (
        <>
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6 text-sm sm:text-base">
            <p>✅ API integration working! Found {grants.length} grants.</p>
            <p className="mt-2 text-xs sm:text-sm">
              API Status: <a href="https://navimpact-api.onrender.com/api/v1/grants/" target="_blank" className="underline">Check API</a>
            </p>
          </div>

      {/* Filters Section - Mobile Optimized */}
      {showFilters && (
        <div className="bg-white border border-gray-200 rounded-lg p-4 sm:p-6 mb-6 shadow-sm">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Search */}
            <div className="sm:col-span-2 lg:col-span-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
              <input
                type="text"
                placeholder="Search grants..."
                value={filters.search}
                onChange={(e) => updateFilter('search', e.target.value)}
                className="w-full px-3 py-3 sm:py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-base"
              />
            </div>

            {/* Deadline */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Deadline</label>
              <select
                value={filters.deadline}
                onChange={(e) => updateFilter('deadline', e.target.value)}
                className="w-full px-3 py-3 sm:py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-base"
              >
                <option value="">All Deadlines</option>
                <option value="closing-soon">Closing Soon (≤7 days)</option>
                <option value="this-month">This Month</option>
                <option value="next-3-months">Next 3 Months</option>
              </select>
            </div>

            {/* Status */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select
                value={filters.status}
                onChange={(e) => updateFilter('status', e.target.value)}
                className="w-full px-3 py-3 sm:py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-base"
              >
                <option value="">All Statuses</option>
                <option value="open">Open</option>
                <option value="active">Active</option>
                <option value="closed">Closed</option>
                <option value="draft">Draft</option>
              </select>
            </div>

            {/* Industry */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Industry</label>
              <select
                value={filters.industry}
                onChange={(e) => updateFilter('industry', e.target.value)}
                className="w-full px-3 py-3 sm:py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-base"
              >
                <option value="">All Industries</option>
                <option value="technology">Technology</option>
                <option value="healthcare">Healthcare</option>
                <option value="education">Education</option>
                <option value="environment">Environment</option>
                <option value="agriculture">Agriculture</option>
                <option value="manufacturing">Manufacturing</option>
                <option value="services">Services</option>
                <option value="research">Research</option>
              </select>
            </div>
          </div>

          {/* Amount Range - Mobile Optimized */}
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">Funding Amount Range</label>
            <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
              <div className="flex-1 sm:flex-none">
                <input
                  type="number"
                  placeholder="Min Amount"
                  value={filters.minAmount}
                  onChange={(e) => updateFilter('minAmount', parseInt(e.target.value) || 0)}
                  className="w-full sm:w-32 px-3 py-3 sm:py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-base"
                />
              </div>
              <span className="text-gray-500 text-center sm:text-left">to</span>
              <div className="flex-1 sm:flex-none">
                <input
                  type="number"
                  placeholder="Max Amount"
                  value={filters.maxAmount}
                  onChange={(e) => updateFilter('maxAmount', parseInt(e.target.value) || 1000000)}
                  className="w-full sm:w-32 px-3 py-3 sm:py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-base"
                />
              </div>
            </div>
          </div>

          {/* Clear Filters */}
          <div className="mt-4 flex justify-center sm:justify-end">
            <button
              onClick={clearFilters}
              className="text-gray-600 hover:text-gray-800 text-sm font-medium px-4 py-2 rounded-md hover:bg-gray-100 transition-colors"
            >
              Clear All Filters
            </button>
          </div>
        </div>
      )}

      {/* Results Summary - Mobile Optimized */}
      <div className="mb-6">
        <p className="text-sm sm:text-base text-gray-600 text-center sm:text-left">
          Showing {filteredGrants.length} of {grants.length} grants
          {filters.search && ` matching "${filters.search}"`}
        </p>
      </div>

      {filteredGrants.length === 0 ? (
        <div className="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded text-center sm:text-left">
          <p className="text-sm sm:text-base">No grants match your current filters. Try adjusting your search criteria.</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {filteredGrants.map((grant) => {
            const deadlineInfo = grant.deadline ? getDeadlineCountdown(grant.deadline) : null;
            const isExpanded = expandedGrants.has(grant.id);
            
            return (
              <div key={grant.id} className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
                {/* Header - Mobile Optimized */}
                <div className="p-4 sm:p-6 border-b border-gray-100">
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="text-base sm:text-lg font-semibold text-gray-900 line-clamp-2 leading-tight flex-1 mr-3">
                      {grant.title}
                    </h3>
                    <div className="flex-shrink-0 flex items-center space-x-2">
                      {getUrgencyBadge(grant.deadline) && (
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getUrgencyBadge(grant.deadline)?.color}`}>
                          <span className="mr-1">{getUrgencyBadge(grant.deadline)?.icon}</span>
                          {getUrgencyBadge(grant.deadline)?.text}
                        </span>
                      )}
                      {getStatusBadge(grant.status)}
                </div>
                  </div>
                  
                  {/* Key Info - Mobile Optimized */}
                  <div className="space-y-2">
                    <div className="flex items-center text-xs sm:text-sm text-gray-600">
                      <span className="font-medium">Source:</span>
                      <span className="ml-2 truncate">{grant.source}</span>
                    </div>
                    
                    <div className="flex items-center text-xs sm:text-sm text-gray-600">
                      <span className="font-medium">Funding:</span>
                      <span className="ml-2 font-semibold text-gray-900">
                        {formatAmount(grant.min_amount, grant.max_amount)}
                    </span>
                  </div>
                  
                    {deadlineInfo && (
                      <div className="flex items-center text-xs sm:text-sm">
                        <span className="font-medium text-gray-600">Deadline:</span>
                        <span className={`ml-2 font-semibold ${deadlineInfo.color}`}>
                          {deadlineInfo.text}
                    </span>
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Micro-Insights Section */}
                <div className="px-4 sm:px-6 py-3 bg-blue-50 border-b border-blue-100">
                  {/* Quick Summary */}
                  <div className="mb-3">
                    {(() => {
                      const summary = getQuickSummary(grant);
                      return (
                        <div className="space-y-1">
                          <div className="flex items-start text-xs sm:text-sm">
                            <span className="font-medium text-blue-900 mr-2">👥 For:</span>
                            <span className="text-blue-800">{summary.who}</span>
                          </div>
                          <div className="flex items-start text-xs sm:text-sm">
                            <span className="font-medium text-blue-900 mr-2">🎯 Why:</span>
                            <span className="text-blue-800">{summary.why}</span>
                          </div>
                          <div className="flex items-start text-xs sm:text-sm">
                            <span className="font-medium text-blue-900 mr-2">💡 Key:</span>
                            <span className="text-blue-800">{summary.key}</span>
                          </div>
                        </div>
                      );
                    })()}
                  </div>

                  {/* Sector Relevance */}
                  {getSectorRelevance(grant) && (
                    <div className="flex items-center text-xs sm:text-sm text-blue-700">
                      <span className="mr-1">🔗</span>
                      <span>{getSectorRelevance(grant)?.text}</span>
                    </div>
                  )}
                </div>
                
                {/* Description - Mobile Optimized */}
                <div className="p-4 sm:p-6">
                  <p className="text-gray-600 text-xs sm:text-sm line-clamp-3 leading-relaxed">
                    {grant.description}
                  </p>
                  
                  {/* Expandable Details - Mobile Optimized */}
                  {isExpanded && (
                    <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
                      {grant.industry_focus && (
                        <div className="flex flex-col sm:flex-row sm:items-center text-xs sm:text-sm">
                          <span className="font-medium text-gray-600 sm:w-20 mb-1 sm:mb-0">Industry:</span>
                          <span className="text-gray-900">{grant.industry_focus}</span>
        </div>
      )}

                      {grant.location_eligibility && (
                        <div className="flex flex-col sm:flex-row sm:items-center text-xs sm:text-sm">
                          <span className="font-medium text-gray-600 sm:w-20 mb-1 sm:mb-0">Location:</span>
                          <span className="text-gray-900">{grant.location_eligibility}</span>
            </div>
                      )}
                      
                      {grant.org_type_eligible && grant.org_type_eligible.length > 0 && (
                        <div className="flex flex-col sm:flex-row sm:items-start text-xs sm:text-sm">
                          <span className="font-medium text-gray-600 sm:w-20 mb-1 sm:mb-0">Eligible:</span>
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
                  
                  {/* Action Buttons - Mobile Optimized */}
                  <div className="mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
                    <button
                      onClick={() => toggleExpanded(grant.id)}
                      className="text-xs sm:text-sm text-blue-600 hover:text-blue-800 font-medium text-center sm:text-left"
                    >
                      {isExpanded ? 'Show Less' : 'More Details'}
                    </button>
                    
                    <div className="flex justify-center sm:justify-end space-x-4">
                      <button className="text-xs sm:text-sm text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md hover:bg-gray-100 transition-colors">
                        📌 Save
                      </button>
                      <button className="text-xs sm:text-sm text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md hover:bg-gray-100 transition-colors">
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

      {/* Grant Comparison Modal */}
      {showComparison && (
        <GrantComparison
          grants={filteredGrants}
          onClose={() => setShowComparison(false)}
        />
      )}
        </>
      )}
    </div>
  );
} 