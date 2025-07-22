import { Grant } from '@/types/models';
import { UserProfile } from './profile';

export interface GrantMatch {
  grant: Grant;
  score: number; // 0-100
  reasons: string[];
  priority: 'high' | 'medium' | 'low';
}

export interface MatchingCriteria {
  organisationType: number;
  industryFocus: number;
  location: number;
  fundingRange: number;
  deadline: number;
  purpose: number;
}

export const DEFAULT_MATCHING_CRITERIA: MatchingCriteria = {
  organisationType: 25, // 25% weight
  industryFocus: 20,    // 20% weight
  location: 15,         // 15% weight
  fundingRange: 20,     // 20% weight
  deadline: 10,         // 10% weight
  purpose: 10,          // 10% weight
};

export class GrantMatchingService {
  private criteria: MatchingCriteria;

  constructor(criteria: Partial<MatchingCriteria> = {}) {
    this.criteria = { ...DEFAULT_MATCHING_CRITERIA, ...criteria };
  }

  /**
   * Calculate matching score between a grant and user profile
   */
  calculateMatch(grant: Grant, profile: UserProfile): GrantMatch {
    const scores = {
      organisationType: this.calculateOrganisationTypeScore(grant, profile),
      industryFocus: this.calculateIndustryFocusScore(grant, profile),
      location: this.calculateLocationScore(grant, profile),
      fundingRange: this.calculateFundingRangeScore(grant, profile),
      deadline: this.calculateDeadlineScore(grant, profile),
      purpose: this.calculatePurposeScore(grant, profile),
    };

    const totalScore = Object.entries(scores).reduce((total, [key, score]) => {
      return total + (score * this.criteria[key as keyof MatchingCriteria]);
    }, 0) / 100;

    const reasons = this.generateReasons(scores, grant, profile);
    const priority = this.determinePriority(totalScore);

    return {
      grant,
      score: Math.round(totalScore),
      reasons,
      priority,
    };
  }

  /**
   * Match multiple grants against a user profile
   */
  matchGrants(grants: Grant[], profile: UserProfile): GrantMatch[] {
    return grants
      .map(grant => this.calculateMatch(grant, profile))
      .sort((a, b) => b.score - a.score); // Sort by score descending
  }

  /**
   * Get top matching grants
   */
  getTopMatches(grants: Grant[], profile: UserProfile, limit: number = 10): GrantMatch[] {
    return this.matchGrants(grants, profile).slice(0, limit);
  }

  private calculateOrganisationTypeScore(grant: Grant, profile: UserProfile): number {
    if (!grant.org_type_eligible || !profile.organisation_type) return 0;

    const eligibleTypes = grant.org_type_eligible.map(type => type.toLowerCase());
    const userType = profile.organisation_type.toLowerCase();

    // Direct match
    if (eligibleTypes.includes(userType)) return 100;

    // Check preferred org types
    if (profile.preferred_org_types) {
      const preferredTypes = profile.preferred_org_types.map(type => type.toLowerCase());
      const hasPreferredMatch = eligibleTypes.some(type => 
        preferredTypes.some(preferred => type.includes(preferred) || preferred.includes(type))
      );
      if (hasPreferredMatch) return 80;
    }

    // Partial match
    const hasPartialMatch = eligibleTypes.some(type => 
      type.includes(userType) || userType.includes(type)
    );
    if (hasPartialMatch) return 60;

    return 0;
  }

  private calculateIndustryFocusScore(grant: Grant, profile: UserProfile): number {
    if (!grant.industry_focus) return 50; // Neutral if no industry specified

    const grantIndustry = grant.industry_focus.toLowerCase();
    const userIndustry = profile.industry_focus?.toLowerCase();

    if (!userIndustry) return 50;

    // Direct match
    if (grantIndustry === userIndustry) return 100;

    // Check preferred industries
    if (profile.preferred_industries) {
      const preferredIndustries = profile.preferred_industries.map(industry => industry.toLowerCase());
      const hasPreferredMatch = preferredIndustries.some(industry => 
        industry.includes(grantIndustry) || grantIndustry.includes(industry)
      );
      if (hasPreferredMatch) return 85;
    }

    // Partial match
    const hasPartialMatch = grantIndustry.includes(userIndustry) || userIndustry.includes(grantIndustry);
    if (hasPartialMatch) return 70;

    return 30;
  }

  private calculateLocationScore(grant: Grant, profile: UserProfile): number {
    if (!grant.location_eligibility) return 50; // Neutral if no location specified

    const grantLocation = grant.location_eligibility.toLowerCase();
    const userLocation = profile.location?.toLowerCase();

    if (!userLocation) return 50;

    // Direct match
    if (grantLocation === userLocation) return 100;

    // Check preferred locations
    if (profile.preferred_locations) {
      const preferredLocations = profile.preferred_locations.map(location => location.toLowerCase());
      const hasPreferredMatch = preferredLocations.some(location => 
        location.includes(grantLocation) || grantLocation.includes(location)
      );
      if (hasPreferredMatch) return 85;
    }

    // Check for national/international grants
    if (grantLocation.includes('national') || grantLocation.includes('australia')) {
      return 80; // Good for most Australian organisations
    }

    // Partial match
    const hasPartialMatch = grantLocation.includes(userLocation) || userLocation.includes(grantLocation);
    if (hasPartialMatch) return 70;

    return 30;
  }

  private calculateFundingRangeScore(grant: Grant, profile: UserProfile): number {
    if (!grant.min_amount && !grant.max_amount) return 50;

    const grantMin = grant.min_amount || 0;
    const grantMax = grant.max_amount || Number.MAX_SAFE_INTEGER;
    const grantAvg = (grantMin + grantMax) / 2;

    const userMin = profile.min_grant_amount || 0;
    const userMax = profile.max_grant_amount || Number.MAX_SAFE_INTEGER;

    // Perfect match within range
    if (grantAvg >= userMin && grantAvg <= userMax) return 100;

    // Close match (within 20% of range)
    const range = userMax - userMin;
    const tolerance = range * 0.2;
    if (grantAvg >= (userMin - tolerance) && grantAvg <= (userMax + tolerance)) return 80;

    // Within 50% of range
    const widerTolerance = range * 0.5;
    if (grantAvg >= (userMin - widerTolerance) && grantAvg <= (userMax + widerTolerance)) return 60;

    return 20;
  }

  private calculateDeadlineScore(grant: Grant, profile: UserProfile): number {
    if (!grant.deadline) return 50;

    const now = new Date();
    const deadline = new Date(grant.deadline);
    const daysUntilDeadline = Math.ceil((deadline.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

    // Check if within user's preferred deadline range
    const maxDays = profile.max_deadline_days || 365;
    
    if (daysUntilDeadline < 0) return 0; // Already closed
    if (daysUntilDeadline <= maxDays) return 100; // Within preferred range
    if (daysUntilDeadline <= maxDays * 1.5) return 80; // Close to preferred range
    if (daysUntilDeadline <= maxDays * 2) return 60; // Within reasonable range

    return 30; // Far in the future
  }

  private calculatePurposeScore(grant: Grant, profile: UserProfile): number {
    if (!grant.funding_purpose || grant.funding_purpose.length === 0) return 50;

    // This is a simplified version - in a real implementation,
    // you might want to match against user's project descriptions or preferences
    return 70; // Default good score for now
  }

  private generateReasons(scores: Record<string, number>, grant: Grant, profile: UserProfile): string[] {
    const reasons: string[] = [];

    if (scores.organisationType >= 80) {
      reasons.push('Perfect organisation type match');
    } else if (scores.organisationType >= 60) {
      reasons.push('Good organisation type compatibility');
    }

    if (scores.industryFocus >= 80) {
      reasons.push('Excellent industry alignment');
    } else if (scores.industryFocus >= 60) {
      reasons.push('Relevant industry focus');
    }

    if (scores.fundingRange >= 80) {
      reasons.push('Ideal funding range');
    } else if (scores.fundingRange >= 60) {
      reasons.push('Suitable funding amount');
    }

    if (scores.deadline >= 80) {
      reasons.push('Perfect timing for application');
    } else if (scores.deadline >= 60) {
      reasons.push('Reasonable application timeline');
    }

    if (reasons.length === 0) {
      reasons.push('General compatibility');
    }

    return reasons;
  }

  private determinePriority(score: number): 'high' | 'medium' | 'low' {
    if (score >= 80) return 'high';
    if (score >= 60) return 'medium';
    return 'low';
  }
}

// Export a default instance
export const grantMatchingService = new GrantMatchingService(); 