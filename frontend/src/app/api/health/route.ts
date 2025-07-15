import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Log environment information
    console.log('Environment:', process.env.NODE_ENV);
    console.log('Backend URL:', process.env.NEXT_PUBLIC_API_URL || process.env.BACKEND_URL);
    
    // Check backend connectivity
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 
                      process.env.BACKEND_URL || 
                      'https://sge-dashboard-backend.onrender.com';
    console.log('Attempting backend health check at:', backendUrl);
    
    const backendHealth = await fetch(`${backendUrl}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Add timeout to prevent hanging
      signal: AbortSignal.timeout(5000)
    });

    console.log('Backend health check status:', backendHealth.status);
    
    if (!backendHealth.ok) {
      const response = {
        status: 'degraded',
        frontend: 'healthy',
        backend: 'unhealthy',
        backend_status: backendHealth.status,
        timestamp: new Date().toISOString(),
      };
      console.log('Health check response (degraded):', response);
      return NextResponse.json(response, { status: 200 });
    }

    const response = {
      status: 'healthy',
      frontend: 'healthy',
      backend: 'healthy',
      timestamp: new Date().toISOString(),
    };
    console.log('Health check response (healthy):', response);
    return NextResponse.json(response, { status: 200 });

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.error('Health check failed:', {
      error: errorMessage,
      stack: error instanceof Error ? error.stack : undefined,
      timestamp: new Date().toISOString()
    });
    
    return NextResponse.json({
      status: 'degraded',
      frontend: 'healthy',
      backend: 'unreachable',
      error: errorMessage,
      timestamp: new Date().toISOString(),
    }, { status: 200 });
  }
} 