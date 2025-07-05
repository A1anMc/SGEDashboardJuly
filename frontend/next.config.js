/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost'],
  },
  headers: async () => {
    const isDev = process.env.NODE_ENV === 'development';
    
    if (isDev) {
      // Very permissive CSP for development - allows everything Next.js needs
      return [
        {
          source: '/:path*',
          headers: [
            {
              key: 'Content-Security-Policy',
              value: [
                "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob: *",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob: *",
                "style-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob: *",
                "img-src 'self' data: blob: *",
                "font-src 'self' data: blob: *",
                "connect-src 'self' http: https: ws: wss: *",
                "frame-src 'self' *",
                "object-src 'self' *",
                "base-uri 'self'",
                "form-action 'self' *",
              ].join('; '),
            },
          ],
        },
      ];
    }
    
    // More restrictive CSP for production
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: [
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
            ].join('; '),
          },
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
        ],
      },
    ];
  },
}

module.exports = nextConfig