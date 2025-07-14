import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  
  // Adjust this value in production, or use tracesSampler for greater control
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.2 : 1.0,
  
  // Setting this option to true will print useful information to the console while you're setting up Sentry.
  debug: process.env.NODE_ENV === 'development',
  
  // Ignore common Next.js errors
  ignoreErrors: [
    // Network errors
    'Failed to fetch',
    'NetworkError',
    'Network request failed',
    // Cancel errors
    'AbortError',
    'Operation was aborted',
    // Navigation errors
    'NEXT_REDIRECT',
    'NEXT_NOT_FOUND',
    // Common browser extensions
    'ResizeObserver loop',
    'ResizeObserver loop completed with undelivered notifications',
  ],
}); 