import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    // Get the backend URL from environment
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 
                      process.env.BACKEND_URL || 
                      'https://sge-dashboard-api.onrender.com';
    
    // Get query parameters from the request
    const { searchParams } = new URL(request.url);
    const queryString = searchParams.toString();
    
    // Construct the backend API URL
    const apiUrl = `${backendUrl}/api/v1/projects/${queryString ? `?${queryString}` : ''}`;
    
    console.log('[API Proxy] Fetching projects from:', apiUrl);
    
    // Forward the request to the backend
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'SGE-Dashboard-Frontend/1.0',
      },
      cache: 'no-store', // Ensure fresh data
    });
    
    if (!response.ok) {
      console.error('[API Proxy] Backend error:', response.status, response.statusText);
      return NextResponse.json(
        { error: 'Failed to fetch projects from backend', status: response.status },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log('[API Proxy] Projects fetched successfully:', data.total || 0, 'items');
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('[API Proxy] Error fetching projects:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    // Get the backend URL from environment
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 
                      process.env.BACKEND_URL || 
                      'https://sge-dashboard-api.onrender.com';
    
    // Get the request body
    const body = await request.json();
    
    // Construct the backend API URL
    const apiUrl = `${backendUrl}/api/v1/projects/`;
    
    console.log('[API Proxy] Creating project at:', apiUrl);
    
    // Forward the request to the backend
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'SGE-Dashboard-Frontend/1.0',
      },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      console.error('[API Proxy] Backend error:', response.status, response.statusText);
      return NextResponse.json(
        { error: 'Failed to create project', status: response.status },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log('[API Proxy] Project created successfully:', data.id);
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('[API Proxy] Error creating project:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 