/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost'],
  },
  // Set default port to 3000
  env: {
    PORT: process.env.PORT || '3000'
  },
  headers: async () => {
    const port = process.env.PORT || '3000';
    const isDev = process.env.NODE_ENV === 'development';
    
    // More permissive CSP for development
    const devCSP = [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval' 'unsafe-inline' data: blob:",
      "style-src 'self' 'unsafe-inline' data: blob:",
      "img-src 'self' data: blob: https:",
      "font-src 'self' data: blob:",
      "connect-src 'self' http: https: ws: wss:",
      "frame-src 'self'",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
    ].join('; ');

    // More restrictive CSP for production
    const prodCSP = [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval' 'unsafe-inline'",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: https:",
      "font-src 'self' data:",
      "connect-src 'self' https:",
      "frame-ancestors 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      "object-src 'none'",
      "upgrade-insecure-requests",
    ].join('; ');

    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: isDev ? devCSP : prodCSP,
          },
          ...(isDev ? [] : [
            {
              key: 'X-Frame-Options',
              value: 'DENY',
            },
            {
              key: 'X-Content-Type-Options',
              value: 'nosniff',
            },
            {
              key: 'Referrer-Policy',
              value: 'strict-origin-when-cross-origin',
            },
            {
              key: 'Strict-Transport-Security',
              value: 'max-age=31536000; includeSubDomains; preload',
            },
          ]),
        ],
      },
    ];
  },
}

module.exports = nextConfig