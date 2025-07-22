'use client';

import { useState, useEffect } from 'react';
import { UserProfile, profileService } from '@/services/profile';
import ProfileForm from '@/components/profile/ProfileForm';
import Avatar from '@/components/ui/avatar';

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const userProfile = await profileService.getMyProfile();
      setProfile(userProfile);
    } catch (err) {
      if (err instanceof Error && err.message.includes('404')) {
        // Profile doesn't exist yet, show create form
        setShowForm(true);
      } else {
        setError(err instanceof Error ? err.message : 'Failed to load profile');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSave = (savedProfile: UserProfile) => {
    setProfile(savedProfile);
    setShowForm(false);
  };

  const handleCancel = () => {
    setShowForm(false);
  };

  if (loading) {
    return (
      <div className="container mx-auto p-4 sm:p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading profile...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error && !showForm) {
    return (
      <div className="container mx-auto p-4 sm:p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-red-900 mb-2">Error Loading Profile</h2>
            <p className="text-red-800 mb-4">{error}</p>
            <button
              onClick={loadProfile}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (showForm) {
    return (
      <div className="container mx-auto p-4 sm:p-6">
        <ProfileForm
          profile={profile || undefined}
          onSave={handleSave}
          onCancel={handleCancel}
          mode={profile ? 'edit' : 'create'}
        />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 sm:p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
          <div className="flex items-center gap-4">
            <Avatar 
              email="alan.mccarthy@example.com" 
              name="Alan McCarthy" 
              size="xl" 
              className="border-4 border-gray-200"
            />
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Profile</h1>
              <p className="text-sm sm:text-base text-gray-600">Manage your organisation profile and grant preferences</p>
            </div>
          </div>
          <button
            onClick={() => setShowForm(true)}
            className="mt-4 sm:mt-0 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Edit Profile
          </button>
        </div>

        {/* Profile Display */}
        {profile && (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            {/* Organisation Information */}
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Organisation Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Organisation Name</label>
                  <p className="text-gray-900 font-medium">{profile.organisation_name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Organisation Type</label>
                  <p className="text-gray-900">{profile.organisation_type}</p>
                </div>
                {profile.industry_focus && (
                  <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">Industry Focus</label>
                    <p className="text-gray-900">{profile.industry_focus}</p>
                  </div>
                )}
                {profile.location && (
                  <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">Location</label>
                    <p className="text-gray-900">{profile.location}</p>
                  </div>
                )}
                {profile.website && (
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-600 mb-1">Website</label>
                    <a
                      href={profile.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 underline"
                    >
                      {profile.website}
                    </a>
                  </div>
                )}
                {profile.description && (
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-600 mb-1">Description</label>
                    <p className="text-gray-900">{profile.description}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Grant Preferences */}
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Grant Preferences</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Funding Range</label>
                  <p className="text-gray-900">
                    ${profile.preferred_funding_range_min?.toLocaleString() || '0'} - 
                    ${profile.preferred_funding_range_max?.toLocaleString() || 'No limit'}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Maximum Deadline</label>
                  <p className="text-gray-900">{profile.max_deadline_days} days</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Deadline Alerts</label>
                  <p className="text-gray-900">{profile.deadline_alerts} days before</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Email Notifications</label>
                  <p className="text-gray-900 capitalize">{profile.email_notifications}</p>
                </div>
              </div>
            </div>

            {/* Preferences Arrays */}
            {(profile.preferred_industries?.length || profile.preferred_locations?.length || profile.preferred_org_types?.length) && (
              <div className="p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Additional Preferences</h2>
                <div className="space-y-4">
                  {profile.preferred_industries?.length && (
                    <div>
                      <label className="block text-sm font-medium text-gray-600 mb-2">Preferred Industries</label>
                      <div className="flex flex-wrap gap-2">
                        {profile.preferred_industries.map((industry, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                          >
                            {industry}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {profile.preferred_locations?.length && (
                    <div>
                      <label className="block text-sm font-medium text-gray-600 mb-2">Preferred Locations</label>
                      <div className="flex flex-wrap gap-2">
                        {profile.preferred_locations.map((location, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-800"
                          >
                            {location}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {profile.preferred_org_types?.length && (
                    <div>
                      <label className="block text-sm font-medium text-gray-600 mb-2">Preferred Organisation Types</label>
                      <div className="flex flex-wrap gap-2">
                        {profile.preferred_org_types.map((type, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-purple-100 text-purple-800"
                          >
                            {type}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Timestamps */}
            <div className="p-6 bg-gray-50">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                <div>
                  <span className="font-medium">Created:</span> {new Date(profile.created_at).toLocaleDateString()}
                </div>
                <div>
                  <span className="font-medium">Last Updated:</span> {new Date(profile.updated_at).toLocaleDateString()}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 