export default function SettingsPage() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Settings</h1>
      
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Application Settings</h2>
        
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">API Configuration</h3>
            <p className="text-sm text-gray-600">Backend URL: {process.env.NEXT_PUBLIC_API_URL || 'https://sge-dashboard-api.onrender.com'}</p>
          </div>
          
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Environment</h3>
            <p className="text-sm text-gray-600">Environment: {process.env.NODE_ENV || 'development'}</p>
          </div>
          
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Version</h3>
            <p className="text-sm text-gray-600">Version: 1.0.0</p>
          </div>
        </div>
      </div>
    </div>
  );
} 