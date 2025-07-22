'use client';

import { useState, useEffect } from 'react';
import { UserProfile, UserProfileCreate, UserProfileUpdate, profileService } from '@/services/profile';
import Avatar from '@/components/ui/avatar';

interface ProfileFormProps {
  profile?: UserProfile;
  onSave?: (profile: UserProfile) => void;
  onCancel?: () => void;
  mode?: 'create' | 'edit';
}

const organisationTypes = [
  'Non-profit',
  'Charity',
  'Community Group',
  'Social Enterprise',
  'Government Agency',
  'Educational Institution',
  'Healthcare Organisation',
  'Environmental Group',
  'Arts & Culture',
  'Sports & Recreation',
  'Other'
];

const notificationOptions = [
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
  { value: 'never', label: 'Never' }
];

export default function ProfileForm({ profile, onSave, onCancel, mode = 'edit' }: ProfileFormProps) {
  const [formData, setFormData] = useState<UserProfileCreate>({
    organisation_name: '',
    organisation_type: '',
    industry_focus: '',
    location: '',
    website: '',
    description: '',
    preferred_funding_range_min: undefined,
    preferred_funding_range_max: undefined,
    preferred_industries: [],
    preferred_locations: [],
    preferred_org_types: [],
    max_deadline_days: 90,
    min_grant_amount: 0,
    max_grant_amount: 1000000,
    email_notifications: 'weekly',
    deadline_alerts: 7
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (profile) {
      setFormData({
        organisation_name: profile.organisation_name,
        organisation_type: profile.organisation_type,
        industry_focus: profile.industry_focus || '',
        location: profile.location || '',
        website: profile.website || '',
        description: profile.description || '',
        preferred_funding_range_min: profile.preferred_funding_range_min,
        preferred_funding_range_max: profile.preferred_funding_range_max,
        preferred_industries: profile.preferred_industries || [],
        preferred_locations: profile.preferred_locations || [],
        preferred_org_types: profile.preferred_org_types || [],
        max_deadline_days: profile.max_deadline_days || 90,
        min_grant_amount: profile.min_grant_amount || 0,
        max_grant_amount: profile.max_grant_amount || 1000000,
        email_notifications: profile.email_notifications,
        deadline_alerts: profile.deadline_alerts
      });
    }
  }, [profile]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'number') {
      setFormData(prev => ({
        ...prev,
        [name]: value === '' ? undefined : Number(value)
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleArrayInputChange = (field: keyof UserProfileCreate, value: string) => {
    const currentArray = formData[field] as string[] || [];
    if (value && !currentArray.includes(value)) {
      setFormData(prev => ({
        ...prev,
        [field]: [...currentArray, value]
      }));
    }
  };

  const removeArrayItem = (field: keyof UserProfileCreate, index: number) => {
    const currentArray = formData[field] as string[] || [];
    setFormData(prev => ({
      ...prev,
      [field]: currentArray.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      let result: UserProfile;
      
      if (mode === 'create') {
        result = await profileService.createProfile(formData);
      } else {
        result = await profileService.updateMyProfile(formData as UserProfileUpdate);
      }

      setSuccess(mode === 'create' ? 'Profile created successfully!' : 'Profile updated successfully!');
      onSave?.(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <div className="flex items-center gap-4 mb-6">
        <Avatar 
          email="alan.mccarthy@example.com" 
          name="Alan McCarthy" 
          size="lg" 
          className="border-2 border-gray-200"
        />
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            {mode === 'create' ? 'Create Profile' : 'Edit Profile'}
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            {mode === 'create' ? 'Set up your organisation profile' : 'Update your profile information'}
          </p>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
          <p className="text-green-800">{success}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Organisation Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="organisation_name" className="block text-sm font-medium text-gray-700 mb-2">
              Organisation Name *
            </label>
            <input
              type="text"
              id="organisation_name"
              name="organisation_name"
              value={formData.organisation_name}
              onChange={handleInputChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="organisation_type" className="block text-sm font-medium text-gray-700 mb-2">
              Organisation Type *
            </label>
            <select
              id="organisation_type"
              name="organisation_type"
              value={formData.organisation_type}
              onChange={handleInputChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select organisation type</option>
              {organisationTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="industry_focus" className="block text-sm font-medium text-gray-700 mb-2">
              Industry Focus
            </label>
            <input
              type="text"
              id="industry_focus"
              name="industry_focus"
              value={formData.industry_focus}
              onChange={handleInputChange}
              placeholder="e.g., Healthcare, Education, Environment"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
              Location
            </label>
            <input
              type="text"
              id="location"
              name="location"
              value={formData.location}
              onChange={handleInputChange}
              placeholder="e.g., Sydney, NSW"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div>
          <label htmlFor="website" className="block text-sm font-medium text-gray-700 mb-2">
            Website
          </label>
          <input
            type="url"
            id="website"
            name="website"
            value={formData.website}
            onChange={handleInputChange}
            placeholder="https://example.com"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
            Description
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            rows={3}
                          placeholder="Brief description of your organisation and its mission"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Grant Preferences */}
        <div className="border-t pt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Grant Preferences</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="preferred_funding_range_min" className="block text-sm font-medium text-gray-700 mb-2">
                Minimum Funding Amount
              </label>
              <input
                type="number"
                id="preferred_funding_range_min"
                name="preferred_funding_range_min"
                value={formData.preferred_funding_range_min || ''}
                onChange={handleInputChange}
                min="0"
                placeholder="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label htmlFor="preferred_funding_range_max" className="block text-sm font-medium text-gray-700 mb-2">
                Maximum Funding Amount
              </label>
              <input
                type="number"
                id="preferred_funding_range_max"
                name="preferred_funding_range_max"
                value={formData.preferred_funding_range_max || ''}
                onChange={handleInputChange}
                min="0"
                placeholder="1000000"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            <div>
              <label htmlFor="max_deadline_days" className="block text-sm font-medium text-gray-700 mb-2">
                Maximum Deadline (days)
              </label>
              <input
                type="number"
                id="max_deadline_days"
                name="max_deadline_days"
                value={formData.max_deadline_days || ''}
                onChange={handleInputChange}
                min="1"
                max="365"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label htmlFor="deadline_alerts" className="block text-sm font-medium text-gray-700 mb-2">
                Deadline Alert (days before)
              </label>
              <input
                type="number"
                id="deadline_alerts"
                name="deadline_alerts"
                value={formData.deadline_alerts || ''}
                onChange={handleInputChange}
                min="1"
                max="30"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Notification Preferences */}
        <div className="border-t pt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Notification Preferences</h3>
          
          <div>
            <label htmlFor="email_notifications" className="block text-sm font-medium text-gray-700 mb-2">
              Email Notifications
            </label>
            <select
              id="email_notifications"
              name="email_notifications"
              value={formData.email_notifications}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {notificationOptions.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-4 pt-6 border-t">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Saving...' : (mode === 'create' ? 'Create Profile' : 'Save Changes')}
          </button>
        </div>
      </form>
    </div>
  );
} 