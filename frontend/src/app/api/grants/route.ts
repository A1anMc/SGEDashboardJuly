import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    // Get the backend URL from environment
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 
                      process.env.BACKEND_URL || 
                      'http://localhost:8000';
    
    // Get query parameters from the request
    const { searchParams } = new URL(request.url);
    const queryString = searchParams.toString();
    
    // Construct the backend API URL
    const apiUrl = `${backendUrl}/api/v1/grants/${queryString ? `?${queryString}` : ''}`;
    
    console.log('[API Proxy] Fetching from:', apiUrl);
    
    // Forward the request to the backend
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      console.error('[API Proxy] Backend error:', response.status, response.statusText);
      
      // If it's a 429 (rate limit), pass it through with more info
      if (response.status === 429) {
        const errorData = await response.json().catch(() => ({ error: 'Rate limit exceeded' }));
        return NextResponse.json(
          { 
            error: 'Rate limit exceeded', 
            status: 429,
            message: 'Too many requests. Please try again later.',
            details: errorData
          },
          { status: 429 }
        );
      }
      
      return NextResponse.json(
        { error: 'Backend API error', status: response.status },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('[API Proxy] Success:', data.total || 0, 'grants found');
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('[API Proxy] Error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch grants', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 
                      process.env.BACKEND_URL || 
                      'http://localhost:8000';
    
    const body = await request.json();
    
    const response = await fetch(`${backendUrl}/api/v1/grants/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: 'Backend API error', status: response.status },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('[API Proxy] POST Error:', error);
    return NextResponse.json(
      { error: 'Failed to create grant', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 