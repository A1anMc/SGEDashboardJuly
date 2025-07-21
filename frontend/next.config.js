/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  

  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://navimpact-api.onrender.com',
  },
  
  // Image optimization
  images: {
    domains: ['navimpact-frontend.onrender.com', 'navimpact-api.onrender.com'],
    unoptimized: true, // For better standalone compatibility
  },
  
  // Security headers with development-friendly CSP
  async headers() {
    const isDevelopment = process.env.NODE_ENV === 'development';
    
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          // CSP that allows Next.js to function properly
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://navimpact-api.onrender.com ws: wss:;"
          }
        ],
      },
    ];
  },
};

module.exports = nextConfig;
