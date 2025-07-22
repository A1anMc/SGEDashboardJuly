'use client';

import { useState, useEffect } from 'react';
import { UserProfile, UserProfileCreate, UserProfileUpdate, profileService } from '@/services/profile';

interface ProfileFormProps {
  onSave?: (profile: UserProfile) => void;
  onCancel?: () => void;
  mode?: 'create' | 'edit';
}

export default function ProfileForm({ onSave, onCancel, mode = 'edit' }: ProfileFormProps) {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState<UserProfileCreate>({
    organization_name: '',
    organization_type: '',
    industry_focus: '',
    location: '',
    website: '',
    description: '',
    preferred_funding_range_min: 25000,
    preferred_funding_range_max: 200000,
    preferred_industries: [],
    preferred_locations: [],
    preferred_org_types: [],
    max_deadline_days: 90,
    min_grant_amount: 25000,
    max_grant_amount: 200000,
    email_notifications: 'weekly',
    deadline_alerts: 7,
  });

  // Available options
  const organizationTypes = [
    'Startup', 'SME', 'Nonprofit', 'Social Enterprise', 
    'Research Institution', 'Healthcare Provider', 'Indigenous Business',
    'Government Agency', 'Educational Institution'
  ];

  const industries = [
    'technology', 'healthcare', 'education', 'environment', 
    'agriculture', 'manufacturing', 'services', 'research',
    'digital media', 'innovation', 'sustainability'
  ];

  const locations = [
    'Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide',
    'Canberra', 'Darwin', 'Hobart', 'Regional', 'National'
  ];

  const notificationOptions = [
    { value: 'daily', label: 'Daily' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'monthly', label: 'Monthly' },
    { value: 'none', label: 'None' }
  ];

  useEffect(() => {
    if (mode === 'edit') {
      loadProfile();
    }
  }, [mode]);

  const loadProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await profileService.getProfile();
      setFormData({
        organization_name: response.profile.organization_name,
        organization_type: response.profile.organization_type,
        industry_focus: response.profile.industry_focus || '',
        location: response.profile.location || '',
        website: response.profile.website || '',
        description: response.profile.description || '',
        preferred_funding_range_min: response.profile.preferred_funding_range_min || 25000,
        preferred_funding_range_max: response.profile.preferred_funding_range_max || 200000,
        preferred_industries: response.profile.preferred_industries || [],
        preferred_locations: response.profile.preferred_locations || [],
        preferred_org_types: response.profile.preferred_org_types || [],
        max_deadline_days: response.profile.max_deadline_days || 90,
        min_grant_amount: response.profile.min_grant_amount || 25000,
        max_grant_amount: response.profile.max_grant_amount || 200000,
        email_notifications: response.profile.email_notifications || 'weekly',
        deadline_alerts: response.profile.deadline_alerts || 7,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof UserProfileCreate, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(null);
    setSuccess(null);
  };

  const handleArrayChange = (field: keyof UserProfileCreate, value: string, checked: boolean) => {
    const currentArray = (formData[field] as string[]) || [];
    const newArray = checked 
      ? [...currentArray, value]
      : currentArray.filter(item => item !== value);
    
    setFormData(prev => ({ ...prev, [field]: newArray }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      let response;
      if (mode === 'create') {
        response = await profileService.createProfile(formData);
      } else {
        response = await profileService.updateProfile(formData);
      }

      setSuccess(response.message);
      onSave?.(response.profile);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save profile');
    } finally {
      setSaving(false);
    }
  };

  const handleSeedSample = async () => {
    try {
      setLoading(true);
      const response = await profileService.seedSampleProfile();
      setSuccess(response.message);
      await loadProfile(); // Reload the form with sample data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create sample profile');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">
            {mode === 'create' ? 'Create Your Profile' : 'Edit Profile'}
          </h2>
          <p className="text-gray-600 mt-1">
            {mode === 'create' 
              ? 'Set up your organization profile to get personalized grant recommendations'
              : 'Update your organization details and grant preferences'
            }
          </p>
        </div>

        {/* Messages */}
        {error && (
          <div className="mx-6 mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}
        {success && (
          <div className="mx-6 mt-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
            {success}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-8">
          {/* Organization Details */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Organization Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Organization Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.organization_name}
                  onChange={(e) => handleInputChange('organization_name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter organization name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Organization Type *
                </label>
                <select
                  required
                  value={formData.organization_type}
                  onChange={(e) => handleInputChange('organization_type', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select organization type</option>
                  {organizationTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Industry Focus
                </label>
                <select
                  value={formData.industry_focus}
                  onChange={(e) => handleInputChange('industry_focus', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select industry</option>
                  {industries.map(industry => (
                    <option key={industry} value={industry}>
                      {industry.charAt(0).toUpperCase() + industry.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location
                </label>
                <select
                  value={formData.location}
                  onChange={(e) => handleInputChange('location', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select location</option>
                  {locations.map(location => (
                    <option key={location} value={location}>{location}</option>
                  ))}
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Website
                </label>
                <input
                  type="url"
                  value={formData.website}
                  onChange={(e) => handleInputChange('website', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://your-organization.com"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Brief description of your organization and mission"
                />
              </div>
            </div>
          </div>

          {/* Grant Preferences */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Grant Preferences</h3>
            
            {/* Funding Range */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Preferred Funding Range
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Minimum Amount</label>
                  <input
                    type="number"
                    value={formData.preferred_funding_range_min}
                    onChange={(e) => handleInputChange('preferred_funding_range_min', parseInt(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="25000"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Maximum Amount</label>
                  <input
                    type="number"
                    value={formData.preferred_funding_range_max}
                    onChange={(e) => handleInputChange('preferred_funding_range_max', parseInt(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="200000"
                  />
                </div>
              </div>
            </div>

            {/* Preferred Industries */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Preferred Industries
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {industries.map(industry => (
                  <label key={industry} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.preferred_industries?.includes(industry) || false}
                      onChange={(e) => handleArrayChange('preferred_industries', industry, e.target.checked)}
                      className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">
                      {industry.charAt(0).toUpperCase() + industry.slice(1)}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Preferred Locations */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Preferred Locations
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {locations.map(location => (
                  <label key={location} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.preferred_locations?.includes(location) || false}
                      onChange={(e) => handleArrayChange('preferred_locations', location, e.target.checked)}
                      className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">{location}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Application Preferences */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Deadline Days
                </label>
                <input
                  type="number"
                  value={formData.max_deadline_days}
                  onChange={(e) => handleInputChange('max_deadline_days', parseInt(e.target.value) || 90)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="90"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Notifications
                </label>
                <select
                  value={formData.email_notifications}
                  onChange={(e) => handleInputChange('email_notifications', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {notificationOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Deadline Alerts (days)
                </label>
                <input
                  type="number"
                  value={formData.deadline_alerts}
                  onChange={(e) => handleInputChange('deadline_alerts', parseInt(e.target.value) || 7)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="7"
                />
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row justify-between space-y-3 sm:space-y-0 sm:space-x-4 pt-6 border-t border-gray-200">
            <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
              <button
                type="submit"
                disabled={saving}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {saving ? 'Saving...' : (mode === 'create' ? 'Create Profile' : 'Save Changes')}
              </button>
              
              {mode === 'create' && (
                <button
                  type="button"
                  onClick={handleSeedSample}
                  disabled={loading}
                  className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? 'Creating...' : 'Create Sample Profile'}
                </button>
              )}
            </div>
            
            {onCancel && (
              <button
                type="button"
                onClick={onCancel}
                className="bg-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-400 transition-colors"
              >
                Cancel
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
} 