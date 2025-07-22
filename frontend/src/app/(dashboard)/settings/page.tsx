import Link from 'next/link';

export default function SettingsPage() {
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-4">Settings</h1>
      <p className="text-gray-600 mb-4">Configure your NavImpact preferences</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Profile Settings */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Profile</h2>
          <p className="text-gray-600 mb-4">Manage your organisation profile and grant preferences</p>
          <Link 
            href="/settings/profile"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Manage Profile
          </Link>
        </div>

        {/* Coming Soon */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Notifications</h2>
          <p className="text-gray-600 mb-4">Configure email and deadline alerts</p>
          <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-3 py-2 rounded text-sm">
            Coming soon
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Preferences</h2>
          <p className="text-gray-600 mb-4">Customise your dashboard and display options</p>
          <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-3 py-2 rounded text-sm">
            Coming soon
          </div>
        </div>
      </div>
    </div>
  );
} 