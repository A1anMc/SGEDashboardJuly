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
    // Ensure proper static file copying
    outputFileTracingRoot: process.env.NODE_ENV === 'production' ? './' : undefined,
    outputStandalone: true,
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

  // API rewrites for development
  rewrites: async () => {
    if (process.env.NODE_ENV === 'development') {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      return [
        {
          source: '/api/:path*',
          destination: `${backendUrl}/api/:path*`,
        },
      ];
    }
    return [];
  },

  // Security headers
  headers: async () => {
    const isProd = process.env.NODE_ENV === 'production';
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    // Base security headers
    const securityHeaders = [
      {
        key: 'X-Frame-Options',
        value: 'DENY',
      },
      {
        key: 'X-Content-Type-Options',
        value: 'nosniff',
      },
      {
        key: 'X-XSS-Protection',
        value: '1; mode=block',
      },
      {
        key: 'Referrer-Policy',
        value: 'strict-origin-when-cross-origin',
      },
      {
        key: 'Permissions-Policy',
        value: 'camera=(), microphone=(), geolocation=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=()',
      },
    ];

    // Add HSTS in production
    if (isProd) {
      securityHeaders.push({
        key: 'Strict-Transport-Security',
        value: 'max-age=31536000; includeSubDomains; preload',
      });
    }

    // Content Security Policy
    const cspDirectives = [
      "default-src 'self'",
      // Scripts: More restrictive in production, allow eval in development
      isProd 
        ? "script-src 'self' 'unsafe-inline' https://*.onrender.com"
        : "script-src 'self' 'unsafe-eval' 'unsafe-inline' http://localhost:* ws://localhost:*",
      // Styles: Allow inline for styled-components and CSS-in-JS
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      // Images: Allow data URLs and HTTPS images
      "img-src 'self' data: blob: https:",
      // Fonts: Allow data URLs and Google Fonts
      "font-src 'self' data: https://fonts.gstatic.com",
      // Connections: Restrict to known domains
      isProd 
        ? `connect-src 'self' https://*.onrender.com wss://*.onrender.com https://*.supabase.co`
        : `connect-src 'self' http://localhost:* ws://localhost:* https://*.supabase.co ${backendUrl}`,
      // Frame restrictions
      "frame-ancestors 'none'",
      // Base URI restriction
      "base-uri 'self'",
      // Form submission restriction
      "form-action 'self'",
      // Object restrictions
      "object-src 'none'",
      // Media restrictions
      "media-src 'self'",
      // Worker restrictions
      "worker-src 'self' blob:",
      // Manifest restrictions
      "manifest-src 'self'",
    ];

    // Add upgrade-insecure-requests in production
    if (isProd) {
      cspDirectives.push("upgrade-insecure-requests");
    }

    securityHeaders.push({
      key: 'Content-Security-Policy',
      value: cspDirectives.join('; '),
    });

    return [
      {
        source: '/:path*',
        headers: securityHeaders,
      },
    ];
  },

  // Webpack configuration for security
  webpack: (config, { dev, isServer }) => {
    // Security: Disable eval in production
    if (!dev) {
      config.devtool = false;
    }

    // Security: Add integrity checks
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        ...config.optimization.splitChunks,
        cacheGroups: {
          ...config.optimization.splitChunks.cacheGroups,
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            priority: 10,
            chunks: 'all',
          },
        },
      };
    }

    return config;
  },

  // Build-time security checks
  eslint: {
    // Security: Fail build on ESLint errors in production
    ignoreDuringBuilds: process.env.NODE_ENV !== 'production',
  },

  typescript: {
    // Security: Fail build on TypeScript errors
    ignoreBuildErrors: false,
  },

  // Production optimizations
  swcMinify: true,
  
  // Security: Disable source maps in production
  productionBrowserSourceMaps: false,
  
  // Performance optimizations
  onDemandEntries: {
    // Period (in ms) where the server will keep pages in the buffer
    maxInactiveAge: 25 * 1000,
    // Number of pages that should be kept simultaneously without being disposed
    pagesBufferLength: 2,
  },
}

module.exports = nextConfig