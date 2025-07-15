/** @type {import('next').NextConfig} */

// Conditionally load bundle analyzer only when needed
const withBundleAnalyzer = process.env.ANALYZE === 'true' 
  ? require('@next/bundle-analyzer')({ enabled: true })
  : (config) => config;

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
      ? ['sge-dashboard-web.onrender.com', 'sge-dashboard-backend.onrender.com']
      : ['localhost', '127.0.0.1'],
    dangerouslyAllowSVG: false,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },
  
  // Environment variables (non-sensitive only)
  env: {
    BACKEND_URL: process.env.NEXT_PUBLIC_API_URL || (
      process.env.NODE_ENV === 'production' 
        ? 'https://sge-dashboard-backend.onrender.com'
        : 'http://localhost:8000'
    ),
    ENVIRONMENT: process.env.NODE_ENV || 'development',
  },

  // Security headers with enhanced CSP
  headers: async () => {
    const isProd = process.env.NODE_ENV === 'production';
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 
      (isProd ? 'https://sge-dashboard-backend.onrender.com' : 'http://localhost:8000');
    
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

  // Optimized webpack configuration
  webpack: (config, { dev, isServer }) => {
    if (!dev && !isServer) {
      // Optimize chunk splitting for better caching
      config.optimization.splitChunks = {
        chunks: 'all',
        minSize: 20000,
        maxSize: 200000, // Reduced from 244000 for better caching
        minChunks: 1,
        maxAsyncRequests: 30,
        maxInitialRequests: 30,
        cacheGroups: {
          // Vendor chunks for better caching
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
            priority: 10,
            reuseExistingChunk: true,
          },
          // Common chunks for shared code
          common: {
            name: 'common',
            minChunks: 2,
            chunks: 'all',
            priority: 5,
            reuseExistingChunk: true,
          },
          // UI framework chunks
          ui: {
            test: /[\\/]node_modules[\\/](@mui|@radix-ui|@headlessui|@heroicons)[\\/]/,
            name: 'ui-vendors',
            chunks: 'all',
            priority: 8,
            reuseExistingChunk: true,
          },
          // Chart and visualization chunks
          charts: {
            test: /[\\/]node_modules[\\/](recharts|framer-motion)[\\/]/,
            name: 'charts-vendors',
            chunks: 'all',
            priority: 7,
            reuseExistingChunk: true,
          },
          // Default fallback
          default: {
            minChunks: 2,
            priority: -20,
            reuseExistingChunk: true,
          },
        },
      };

      // Optimize module resolution
      config.resolve.alias = {
        ...config.resolve.alias,
        // Optimize imports for better tree shaking
        '@': require('path').resolve(__dirname, 'src'),
      };
    }

    // Add bundle analyzer plugin for development analysis
    if (process.env.ANALYZE === 'true') {
      try {
        const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
        config.plugins.push(
          new BundleAnalyzerPlugin({
            analyzerMode: 'static',
            openAnalyzer: false,
            reportFilename: '.next/analyze/bundle-report.html',
          })
        );
      } catch (error) {
        console.warn('Bundle analyzer not available, skipping...');
      }
    }

    return config;
  },

  // Production optimizations
  swcMinify: true,
  productionBrowserSourceMaps: false,
  
  // Experimental optimizations
  experimental: {
    // Enable modern bundling features
    optimizePackageImports: ['@mui/material', '@mui/icons-material', '@radix-ui/react-dialog', '@radix-ui/react-popover'],
  },
}

module.exports = withBundleAnalyzer(nextConfig);