// Frontend configuration
export const config = {
  // API Configuration
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'https://navimpact-api.onrender.com',
  apiVersion: 'v1',
  
  // App Configuration
  appName: process.env.NEXT_PUBLIC_APP_NAME || 'NavImpact',
  appVersion: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
  
  // Environment
  isDevelopment: process.env.NODE_ENV === 'development',
  isProduction: process.env.NODE_ENV === 'production',
  
  // API Endpoints
  endpoints: {
    health: '/health',
    grants: '/api/v1/grants/',
    tasks: '/api/v1/tasks/',
    projects: '/api/v1/projects/',
    users: '/api/v1/users/',
    tags: '/api/v1/tags/',
  }
} as const;

// Helper function to build API URLs
export const buildApiUrl = (endpoint: string, params?: Record<string, string>) => {
  const url = new URL(endpoint, config.apiUrl);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, value);
    });
  }
  return url.toString();
}; 