'use client';

import { useState, useEffect } from 'react';
import ProfileForm from '@/components/profile/ProfileForm';
import { UserProfile, profileService } from '@/services/profile';

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasProfile, setHasProfile] = useState(false);

  useEffect(() => {
    checkProfile();
  }, []);

  const checkProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const exists = await profileService.hasProfile();
      setHasProfile(exists);
      
      if (exists) {
        const response = await profileService.getProfile();
        setProfile(response.profile);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to check profile status');
    } finally {
      setLoading(false);
    }
  };

  const handleProfileSave = (savedProfile: UserProfile) => {
    setProfile(savedProfile);
    setHasProfile(true);
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading profile...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>Error: {error}</p>
          <button
            onClick={checkProfile}
            className="mt-2 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Profile Settings</h1>
        <p className="text-gray-600 mt-2">
          Manage your organization profile and grant preferences
        </p>
      </div>

      {/* Profile Status */}
      {hasProfile && profile && (
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-lg font-semibold text-blue-900">
                {profile.organization_name}
              </h3>
              <p className="text-blue-700 text-sm">
                {profile.organization_type} • {profile.industry_focus || 'No industry specified'}
              </p>
              {profile.location && (
                <p className="text-blue-600 text-sm">📍 {profile.location}</p>
              )}
            </div>
            <div className="text-right">
              <p className="text-xs text-blue-600">
                Last updated: {new Date(profile.updated_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Profile Form */}
      <ProfileForm
        mode={hasProfile ? 'edit' : 'create'}
        onSave={handleProfileSave}
      />

      {/* Help Section */}
      {!hasProfile && (
        <div className="mt-8 bg-gray-50 border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Why Create a Profile?
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">🎯 Personalized Recommendations</h4>
              <p>Get grants that match your organization type, industry, and funding needs.</p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">⚡ Save Time</h4>
              <p>Filter out grants you're not eligible for and focus on relevant opportunities.</p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">📊 Smart Matching</h4>
              <p>See match scores and reasons why grants are recommended for you.</p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">🔔 Better Notifications</h4>
              <p>Get alerts for deadlines and new grants that match your preferences.</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 