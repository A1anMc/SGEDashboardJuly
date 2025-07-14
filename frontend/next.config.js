/** @type {import('next').NextConfig} */
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

const nextConfig = {
  // Production optimization
  output: 'standalone',
  distDir: '.next',
  
  // Security: Disable powered by header
  poweredByHeader: false,
  
  // Compression for better performance
  compress: true,
  
  // Image optimization with security
  images: {
    domains: process.env.NODE_ENV === 'production' 
      ? ['sge-dashboard-web.onrender.com', 'sge-dashboard-api.onrender.com']
      : ['localhost', '127.0.0.1'],
    dangerouslyAllowSVG: false,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },
  
  // Environment variables (non-sensitive only)
  env: {
    BACKEND_URL: process.env.NEXT_PUBLIC_API_URL || (
      process.env.NODE_ENV === 'production' 
        ? 'https://sge-dashboard-api.onrender.com'
        : 'http://localhost:8000'
    ),
    ENVIRONMENT: process.env.NODE_ENV || 'development',
  },

  // Security headers with enhanced CSP
  headers: async () => {
    const isProd = process.env.NODE_ENV === 'production';
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 
      (isProd ? 'https://sge-dashboard-api.onrender.com' : 'http://localhost:8000');
    
    // Base CSP directives
    const baseCSP = {
      'default-src': ["'self'"],
      'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"], // Required for Next.js
      'style-src': ["'self'", "'unsafe-inline'"], // Required for styled-components and CSS-in-JS
      'img-src': ["'self'", 'data:', 'blob:', 'https:'],
      'font-src': ["'self'", 'data:'],
      'connect-src': ["'self'"],
      'frame-ancestors': ["'none'"],
      'base-uri': ["'self'"],
      'form-action': ["'self'"],
      'object-src': ["'none'"],
      'media-src': ["'self'", 'blob:'],
    };

    // Add environment-specific sources
    if (isProd) {
      baseCSP['connect-src'].push(
        'https://*.onrender.com',
        'https://*.supabase.co',
        backendUrl
      );
    } else {
      baseCSP['connect-src'].push(
        'http://localhost:*',
        'ws://localhost:*',
        backendUrl
      );
    }

    // Convert CSP object to string
    const cspString = Object.entries(baseCSP)
      .map(([key, values]) => `${key} ${values.join(' ')}`)
      .join('; ');
    
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=31536000; includeSubDomains; preload'
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block'
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin'
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=(), interest-cohort=()'
          },
          {
            key: 'Content-Security-Policy',
            value: cspString
          }
        ]
      }
    ]
  },

  // Webpack configuration for optimization
  webpack: (config, { dev, isServer }) => {
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        minSize: 20000,
        maxSize: 244000,
        minChunks: 1,
        maxAsyncRequests: 30,
        maxInitialRequests: 30,
        cacheGroups: {
          defaultVendors: {
            test: /[\\/]node_modules[\\/]/,
            priority: -10,
            reuseExistingChunk: true,
          },
          default: {
            minChunks: 2,
            priority: -20,
            reuseExistingChunk: true,
          },
        },
      };
    }
    return config;
  },

  // Production optimizations
  swcMinify: true,
  productionBrowserSourceMaps: false,
}

module.exports = withBundleAnalyzer(nextConfig);