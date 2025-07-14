/** @type {import('next').NextConfig} */

const nextConfig = {
  // Production optimization
  output: 'standalone',
  distDir: '.next',
  
  // Security: Disable powered by header
  poweredByHeader: false,
  
  // Compression for better performance
  compress: true,
  
  // Experimental features
  experimental: {
    // Enable modern bundling
    esmExternals: true,
  },
  
  // Image optimization with security
  images: {
    domains: process.env.NODE_ENV === 'production' 
      ? ['sge-dashboard-web.onrender.com', 'sge-dashboard-api.onrender.com']
      : ['localhost', '127.0.0.1'],
    // Security: Disable external image optimization
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

  // Security headers
  headers: async () => {
    const isProd = process.env.NODE_ENV === 'production';
    
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
            value: 'max-age=31536000; includeSubDomains'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
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
            key: 'Content-Security-Policy',
            value: isProd
              ? "default-src 'self' https://*.onrender.com; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob: https:; font-src 'self' data:; connect-src 'self' https://*.onrender.com https://*.supabase.co"
              : "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self' http://localhost:* ws://localhost:*"
          }
        ]
      }
    ]
  },

  // Webpack configuration for security
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

module.exports = nextConfig