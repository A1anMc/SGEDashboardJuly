# CSP Error Fix - Frontend API Connection Issue

## Problem
You're encountering a Content Security Policy (CSP) error when trying to connect to your backend API:

```
Refused to connect to 'http://127.0.0.1:8000/grants?page=1' because it violates the following Content Security Policy directive: "connect-src 'self' http://localhost:8000".
```

## Root Cause
- Your backend API is configured to use `http://127.0.0.1:8000`
- Your CSP policy only allows connections to `http://localhost:8000`
- While these are the same address, CSP treats them as different origins

## Solution Options

### Option 1: Update API URL to use localhost (Recommended)
Find your `grantsApi.ts` file (likely in `src/services/` or similar) and change the base URL:

```typescript
// Change from:
const API_BASE_URL = 'http://127.0.0.1:8000';

// To:
const API_BASE_URL = 'http://localhost:8000';
```

### Option 2: Update CSP to allow 127.0.0.1
If you have a Next.js configuration file (`next.config.js` or `next.config.ts`), update the CSP:

```javascript
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "connect-src 'self' http://localhost:8000 http://127.0.0.1:8000"
          }
        ]
      }
    ];
  }
};
```

### Option 3: Use Environment Variables (Best Practice)
Create a `.env.local` file in your frontend root:

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Then update your API configuration:

```typescript
// grantsApi.ts or similar
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

## Files to Check and Modify

1. **API Configuration File** (likely `grantsApi.ts` or `api.ts`)
   - Location: `src/services/grantsApi.ts` or similar
   - Change base URL from `127.0.0.1:8000` to `localhost:8000`

2. **Next.js Configuration** (if applicable)
   - Location: `next.config.js` or `next.config.ts`
   - Update CSP headers to allow both domains

3. **Environment Variables**
   - Location: `.env.local` or `.env`
   - Add `NEXT_PUBLIC_API_URL=http://localhost:8000`

## Quick Fix Commands

If you're using a Unix-like system, you can quickly find and fix the issue:

```bash
# Find the API configuration file
find . -name "*.ts" -o -name "*.js" | xargs grep -l "127.0.0.1:8000"

# Replace 127.0.0.1 with localhost in the found files
sed -i 's/127\.0\.0\.1:8000/localhost:8000/g' path/to/your/grantsApi.ts
```

## Prevention
To avoid this issue in the future:
1. Always use `localhost` instead of `127.0.0.1` in development
2. Use environment variables for API URLs
3. Configure CSP properly to allow necessary connections

## Testing
After making the changes:
1. Clear your browser cache
2. Restart your development server
3. Check that the API calls now work without CSP errors