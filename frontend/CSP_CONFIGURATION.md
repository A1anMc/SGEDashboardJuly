# Content Security Policy (CSP) Configuration

## Overview

This document explains the Content Security Policy (CSP) and security headers configuration for the SGE Dashboard frontend.

## Security Headers

### Content Security Policy

The application uses a dynamic CSP that adapts to the environment (development/production):

```javascript
// Base CSP directives (common to all environments)
{
  'default-src': ["'self'"],
  'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
  'style-src': ["'self'", "'unsafe-inline'"],
  'img-src': ["'self'", 'data:', 'blob:', 'https:'],
  'font-src': ["'self'", 'data:'],
  'connect-src': ["'self'"],
  'frame-ancestors': ["'none'"],
  'base-uri': ["'self'"],
  'form-action': ["'self'"],
  'object-src': ["'none'"],
  'media-src': ["'self'", 'blob:']
}
```

#### Production-specific additions:
- `connect-src`: 
  - `https://*.onrender.com` - Backend API
  - `https://*.supabase.co` - Authentication
  - Dynamic backend URL from environment

#### Development-specific additions:
- `connect-src`:
  - `http://localhost:*` - Local development
  - `ws://localhost:*` - WebSocket for hot reload
  - Dynamic backend URL from environment

### Additional Security Headers

1. **Strict-Transport-Security**
   ```
   max-age=31536000; includeSubDomains; preload
   ```
   - Enforces HTTPS
   - 1-year cache duration
   - Includes subdomains
   - Eligible for HSTS preload list

2. **X-Frame-Options**
   ```
   DENY
   ```
   - Prevents clickjacking by disabling iframe embedding

3. **X-Content-Type-Options**
   ```
   nosniff
   ```
   - Prevents MIME type sniffing

4. **X-XSS-Protection**
   ```
   1; mode=block
   ```
   - Legacy XSS protection for older browsers

5. **Referrer-Policy**
   ```
   strict-origin-when-cross-origin
   ```
   - Controls referrer information in requests

6. **Permissions-Policy**
   ```
   camera=(), microphone=(), geolocation=(), interest-cohort=()
   ```
   - Disables potentially sensitive browser features
   - Opts out of FLoC/Privacy Sandbox

## Why These Choices?

1. **script-src includes 'unsafe-inline' and 'unsafe-eval'**
   - Required for Next.js functionality
   - Required for React development tools
   - Required for certain npm packages

2. **style-src includes 'unsafe-inline'**
   - Required for styled-components and CSS-in-JS
   - Required for dynamic styles in React

3. **connect-src configuration**
   - Allows API calls to backend
   - Allows authentication with Supabase
   - Allows WebSocket in development for hot reload

4. **frame-ancestors: 'none'**
   - Stronger protection than X-Frame-Options
   - Modern alternative to X-Frame-Options

## Testing CSP Configuration

1. **Development Testing**
   ```bash
   npm run dev
   ```
   - Check browser console for CSP violations
   - Verify hot reload works
   - Verify API calls work

2. **Production Testing**
   ```bash
   npm run build && npm start
   ```
   - Verify all resources load
   - Check for CSP violations
   - Test all application features

## Common Issues and Solutions

1. **CSP Violation: script-src**
   - Check for dynamically loaded scripts
   - Verify third-party script domains are allowed
   - Consider using nonces for inline scripts

2. **CSP Violation: connect-src**
   - Verify API endpoints are allowed
   - Check WebSocket connections
   - Ensure Supabase domains are allowed

3. **CSP Violation: style-src**
   - Check for dynamically added styles
   - Verify CSS-in-JS compatibility
   - Consider using nonces for inline styles

## Maintenance

1. **Regular Updates**
   - Review CSP directives quarterly
   - Update as new features are added
   - Monitor CSP violation reports

2. **Security Considerations**
   - Keep 'unsafe-inline' and 'unsafe-eval' scoped
   - Regularly review allowed domains
   - Consider implementing CSP reporting

3. **Environment Management**
   - Keep development and production configs separate
   - Use environment variables for dynamic values
   - Document any environment-specific changes