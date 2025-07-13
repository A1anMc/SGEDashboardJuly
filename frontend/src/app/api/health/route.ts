import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Check backend connectivity
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 
                      process.env.BACKEND_URL || 
                      'https://sge-dashboard-api.onrender.com';
    const backendHealth = await fetch(`${backendUrl}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!backendHealth.ok) {
      return NextResponse.json({
        status: 'degraded',
        frontend: 'healthy',
        backend: 'unhealthy',
        timestamp: new Date().toISOString(),
      }, { status: 200 });
    }

    return NextResponse.json({
      status: 'healthy',
      frontend: 'healthy',
      backend: 'healthy',
      timestamp: new Date().toISOString(),
    }, { status: 200 });

  } catch (error) {
    console.error('Health check failed:', error);
    return NextResponse.json({
      status: 'degraded',
      frontend: 'healthy',
      backend: 'unreachable',
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    }, { status: 200 });
  }
} 