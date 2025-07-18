export default function MediaPage() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Media Investments</h1>
      
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Media Investment Tracking</h2>
        <p className="text-gray-600">Track and manage media investment opportunities and campaigns.</p>
        
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border rounded-lg p-4">
            <h3 className="font-semibold text-gray-900">Campaigns</h3>
            <p className="text-sm text-gray-600">Manage active campaigns</p>
          </div>
          
          <div className="border rounded-lg p-4">
            <h3 className="font-semibold text-gray-900">Analytics</h3>
            <p className="text-sm text-gray-600">View performance metrics</p>
          </div>
        </div>
      </div>
    </div>
  );
} 