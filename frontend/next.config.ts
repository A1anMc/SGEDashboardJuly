import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  poweredByHeader: false,
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://sge-dashboard-api.onrender.com',
  },
  
  // Image optimization
  images: {
    domains: ['sge-dashboard-web.onrender.com', 'sge-dashboard-api.onrender.com'],
  },
  
  // Security headers - Remove CSP for now to fix the eval issue
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          // Temporarily remove CSP to fix eval issues
          // { key: 'Content-Security-Policy', value: "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" }
        ],
      },
    ];
  },
};

export default nextConfig;
