'use client';

import { useState, useEffect } from 'react';

export default function GrantsPage() {
  const [grants, setGrants] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [apiTest, setApiTest] = useState<any>(null);

  useEffect(() => {
    const fetchGrants = async () => {
      try {
        console.log('[API Test] Starting API test...');
        setApiTest({ status: 'testing', message: 'Testing API connection...' });
        
        // Test 1: Use Next.js API proxy (should work without CORS issues)
        console.log('[API Test] Testing Next.js API proxy...');
        const proxyResponse = await fetch('/api/grants?skip=0&limit=10');
        console.log('[API Test] Proxy response status:', proxyResponse.status);
        
        if (proxyResponse.ok) {
          const proxyData = await proxyResponse.json();
          console.log('[API Test] Proxy SUCCESS:', proxyData);
          setApiTest({ 
            status: 'success', 
            message: 'Connected via Next.js proxy', 
            data: proxyData 
          });
          setGrants(proxyData.items || []);
          setLoading(false);
          return;
        }
        
        // Test 2: Direct backend call (fallback)
        console.log('[API Test] Testing direct backend call...');
        const directResponse = await fetch('http://localhost:8000/api/v1/grants/?skip=0&limit=10');
        console.log('[API Test] Direct response status:', directResponse.status);
        
        if (directResponse.ok) {
          const directData = await directResponse.json();
          console.log('[API Test] Direct SUCCESS:', directData);
          setApiTest({ 
            status: 'success', 
            message: 'Connected via direct backend call', 
            data: directData 
          });
          setGrants(directData.items || []);
          setLoading(false);
          return;
        }
        
        // Both failed
        setApiTest({ 
          status: 'failed', 
          message: `Both proxy (${proxyResponse.status}) and direct (${directResponse.status}) failed` 
        });
        setError('API connection failed');
        setLoading(false);
        
      } catch (err) {
        console.error('[API Test] Exception:', err);
        setApiTest({ 
          status: 'failed', 
          message: `Exception: ${String(err)}` 
        });
        setError(String(err));
        setLoading(false);
      }
    };

    fetchGrants();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Grants Dashboard</h1>
      
      {/* API Test Results */}
      <div className="mb-6 p-4 bg-gray-100 rounded-lg">
        <h2 className="text-lg font-semibold mb-2">🔧 API Connection Test</h2>
        {apiTest ? (
          <div>
            <p className="mb-2">
              Status: {' '}
              {apiTest.status === 'testing' && '🔄 Testing...'}
              {apiTest.status === 'success' && '✅ SUCCESS'}
              {apiTest.status === 'failed' && '❌ FAILED'}
            </p>
            <p className="text-sm text-gray-600">{apiTest.message}</p>
            {apiTest.data && (
              <div className="mt-2 text-sm">
                <p>Total grants: {apiTest.data.total}</p>
                <p>Items received: {apiTest.data.items?.length || 0}</p>
              </div>
            )}
          </div>
        ) : (
          <p>🔄 Initializing test...</p>
        )}
      </div>

      {/* Grants Display */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold mb-2">📋 Grants Data</h2>
        {loading ? (
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            <span>Loading grants...</span>
          </div>
        ) : error ? (
          <div className="text-red-600">Error: {error}</div>
        ) : (
          <div>
            <p className="mb-4 font-medium">Found {grants.length} grants</p>
            {grants.length > 0 ? (
              <div className="grid gap-4">
                {grants.slice(0, 5).map((grant, index) => (
                  <div key={index} className="p-4 border rounded-lg bg-white shadow-sm">
                    <h3 className="font-semibold text-lg mb-2">{grant.title || 'No title'}</h3>
                    <p className="text-gray-600 mb-2">{grant.description || 'No description'}</p>
                    <div className="text-sm text-gray-500">
                      <p>Amount: ${grant.min_amount?.toLocaleString()} - ${grant.max_amount?.toLocaleString()}</p>
                      <p>Status: {grant.status || 'Unknown'}</p>
                      <p>Deadline: {grant.deadline || 'Not specified'}</p>
                    </div>
                  </div>
                ))}
                {grants.length > 5 && (
                  <div className="text-center text-gray-500 mt-4">
                    ... and {grants.length - 5} more grants
                  </div>
                )}
              </div>
            ) : (
              <p className="text-gray-500">No grants found</p>
            )}
          </div>
        )}
      </div>

      {/* System Status */}
      <div className="p-4 bg-green-100 rounded-lg">
        <h2 className="text-lg font-semibold mb-2">🔍 System Status</h2>
        <p>Frontend: ✅ Loaded and working</p>
        <p>JavaScript: ✅ Executing properly</p>
        <p>Next.js Server: ✅ Running on port 3000</p>
        <p>API Connection: {apiTest?.status === 'success' ? '✅ Connected' : '❌ Not Connected'}</p>
      </div>
    </div>
  );
} 