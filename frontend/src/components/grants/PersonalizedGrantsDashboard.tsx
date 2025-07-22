import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { grantsApi } from '@/services/grants';
import { profileService } from '@/services/profile';
import { grantMatchingService, GrantMatch } from '@/services/grant-matching';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { 
  StarIcon, 
  ClockIcon, 
  CurrencyDollarIcon,
  MapPinIcon,
  BuildingOfficeIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

interface PersonalizedGrantsDashboardProps {
  limit?: number;
  showFilters?: boolean;
}

export const PersonalizedGrantsDashboard: React.FC<PersonalizedGrantsDashboardProps> = ({
  limit = 10,
  showFilters = true
}) => {
  const [filterPriority, setFilterPriority] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const [minScore, setMinScore] = useState(0);

  // Fetch user profile
  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ['user-profile'],
    queryFn: profileService.getMyProfile,
    retry: 1,
  });

  // Fetch grants
  const { data: grantsResponse, isLoading: grantsLoading } = useQuery({
    queryKey: ['grants'],
    queryFn: () => grantsApi.getGrants({ limit: 100 }),
  });

  // Calculate matches
  const [matches, setMatches] = useState<GrantMatch[]>([]);
  const [isCalculating, setIsCalculating] = useState(false);

  useEffect(() => {
    if (profile && grantsResponse?.data) {
      setIsCalculating(true);
      const calculatedMatches = grantMatchingService.getTopMatches(
        grantsResponse.data,
        profile,
        limit * 2 // Get more to allow for filtering
      );
      setMatches(calculatedMatches);
      setIsCalculating(false);
    }
  }, [profile, grantsResponse, limit]);

  // Filter matches
  const filteredMatches = matches.filter(match => {
    if (filterPriority !== 'all' && match.priority !== filterPriority) return false;
    if (match.score < minScore) return false;
    return true;
  }).slice(0, limit);

  const isLoading = profileLoading || grantsLoading || isCalculating;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <LoadingSpinner size="lg" variant="brand" />
        <span className="ml-3 text-gray-600">Calculating your perfect grant matches...</span>
      </div>
    );
  }

  if (!profile) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center">
            <BuildingOfficeIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Profile Required</h3>
            <p className="mt-1 text-sm text-gray-500">
              Please complete your organisation profile to get personalized grant recommendations.
            </p>
            <div className="mt-6">
              <Button href="/settings/profile">
                Complete Profile
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Your Grant Matches</h2>
          <p className="text-gray-600">
            Personalized recommendations for {profile.organisation_name}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="info" className="flex items-center gap-1">
            <ChartBarIcon className="h-4 w-4" />
            {filteredMatches.length} matches
          </Badge>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-4">
              <div>
                <label className="text-sm font-medium text-gray-700">Priority</label>
                <select
                  value={filterPriority}
                  onChange={(e) => setFilterPriority(e.target.value as any)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-impact-teal focus:ring-impact-teal sm:text-sm"
                >
                  <option value="all">All Priorities</option>
                  <option value="high">High Priority</option>
                  <option value="medium">Medium Priority</option>
                  <option value="low">Low Priority</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Minimum Score</label>
                <select
                  value={minScore}
                  onChange={(e) => setMinScore(Number(e.target.value))}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-impact-teal focus:ring-impact-teal sm:text-sm"
                >
                  <option value={0}>Any Score</option>
                  <option value={60}>60%+</option>
                  <option value={70}>70%+</option>
                  <option value={80}>80%+</option>
                  <option value={90}>90%+</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Matches */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredMatches.map((match) => (
          <GrantMatchCard key={match.grant.id} match={match} />
        ))}
      </div>

      {filteredMatches.length === 0 && (
        <Card>
          <CardContent className="p-6 text-center">
            <StarIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No matches found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your filters or complete your profile for better matches.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

interface GrantMatchCardProps {
  match: GrantMatch;
}

const GrantMatchCard: React.FC<GrantMatchCardProps> = ({ match }) => {
  const { grant, score, reasons, priority } = match;

  const priorityColors = {
    high: 'bg-mint-breeze text-green-700 border-mint-breeze/30',
    medium: 'bg-warm-amber text-amber-700 border-warm-amber/30',
    low: 'bg-cool-gray text-gray-700 border-cool-gray/30',
  };

  const scoreColors = {
    high: 'bg-gradient-to-r from-mint-breeze to-green-100',
    medium: 'bg-gradient-to-r from-warm-amber to-yellow-100',
    low: 'bg-gradient-to-r from-cool-gray to-gray-100',
  };

  return (
    <Card className="hover:shadow-lg transition-all duration-300" hover>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg font-semibold text-gray-900 line-clamp-2">
              {grant.title}
            </CardTitle>
            <div className="mt-2 flex items-center space-x-2">
              <Badge variant={priority} className={priorityColors[priority]}>
                {priority} priority
              </Badge>
              <Badge variant="info" className="bg-energy-coral/10 text-energy-coral border-energy-coral/20">
                {score}% match
              </Badge>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Score Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Match Score</span>
            <span className="font-medium text-gray-900">{score}%</span>
          </div>
          <div className={`h-2 rounded-full ${scoreColors[priority]}`}>
            <div
              className="h-full bg-gradient-to-r from-impact-teal to-energy-coral rounded-full transition-all duration-500"
              style={{ width: `${score}%` }}
            />
          </div>
        </div>

        {/* Grant Details */}
        <div className="space-y-2 text-sm">
          {grant.min_amount && grant.max_amount && (
            <div className="flex items-center text-gray-600">
              <CurrencyDollarIcon className="h-4 w-4 mr-2" />
              ${grant.min_amount.toLocaleString()} - ${grant.max_amount.toLocaleString()}
            </div>
          )}
          
          {grant.deadline && (
            <div className="flex items-center text-gray-600">
              <ClockIcon className="h-4 w-4 mr-2" />
              {new Date(grant.deadline).toLocaleDateString()}
            </div>
          )}
          
          {grant.location_eligibility && (
            <div className="flex items-center text-gray-600">
              <MapPinIcon className="h-4 w-4 mr-2" />
              {grant.location_eligibility}
            </div>
          )}
        </div>

        {/* Reasons */}
        <div className="space-y-1">
          <p className="text-xs font-medium text-gray-700">Why this matches:</p>
          <ul className="text-xs text-gray-600 space-y-1">
            {reasons.slice(0, 2).map((reason, index) => (
              <li key={index} className="flex items-start">
                <span className="text-energy-coral mr-1">•</span>
                {reason}
              </li>
            ))}
          </ul>
        </div>

        {/* Actions */}
        <div className="flex space-x-2 pt-2">
          <Button size="sm" className="flex-1">
            View Details
          </Button>
          <Button size="sm" variant="outline">
            Save
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default PersonalizedGrantsDashboard; 