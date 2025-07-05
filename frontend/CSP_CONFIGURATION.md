# Content Security Policy (CSP) Configuration Guide

## Problem
Your site is encountering a CSP error: "Content Security Policy of your site blocks the use of 'eval' in JavaScript". This happens when the CSP prevents the evaluation of arbitrary strings as JavaScript.

## Solutions Implemented

### 1. Current Configuration (next.config.js)
The main `next.config.js` file now includes CSP headers with `unsafe-eval` allowed:

```javascript
script-src 'self' 'unsafe-eval' 'unsafe-inline'
```

**Pros:**
- Quick fix that resolves the eval() blocking issue
- Works with all libraries and development tools
- Allows hot reloading and development features

**Cons:**
- Less secure (allows arbitrary code execution)
- May not pass security audits
- Increases XSS attack surface

### 2. Secure Alternative (next.config.secure.js)
A more secure configuration using nonce-based CSP:

```javascript
script-src 'self' 'nonce-${nonce}' 'strict-dynamic'
```

**Pros:**
- Much more secure
- Prevents most XSS attacks
- Complies with security best practices

**Cons:**
- Requires more setup
- May break some libraries
- More complex to implement

## Implementation Options

### Option A: Use Current Configuration (Recommended for Development)
The current `next.config.js` is ready to use. Just restart your development server:

```bash
npm run dev
```

### Option B: Use Secure Configuration (Recommended for Production)
1. Backup your current config:
   ```bash
   cp next.config.js next.config.backup.js
   ```

2. Replace with secure config:
   ```bash
   cp next.config.secure.js next.config.js
   ```

3. Install uuid dependency:
   ```bash
   npm install uuid
   npm install --save-dev @types/uuid
   ```

### Option C: Environment-Specific Configuration
You can create different configs for development vs production by checking NODE_ENV in your next.config.js.

## CSP Directives Explained

- `default-src 'self'`: Only allow resources from the same origin
- `script-src`: Controls where scripts can be loaded from
- `style-src 'self' 'unsafe-inline'`: Allows inline styles (needed for CSS-in-JS)
- `img-src 'self' data: https:`: Allows images from same origin, data URLs, and HTTPS
- `connect-src`: Controls where you can connect to (APIs, WebSockets, etc.)
- `frame-ancestors 'none'`: Prevents page from being embedded in iframes

## Testing Your CSP

1. Open browser developer tools
2. Go to the Console tab
3. Look for CSP violation errors
4. Adjust the policy as needed

## Common Issues and Solutions

### Issue: "Refused to execute inline script"
**Solution:** Add `'unsafe-inline'` to script-src or use nonces

### Issue: "Refused to load the font"
**Solution:** Ensure font-src includes your font sources

### Issue: "Refused to connect"
**Solution:** Add your API endpoints to connect-src

### Issue: Libraries not working
**Solution:** Some libraries require `'unsafe-eval'` - use the current configuration

## Security Recommendations

1. **Development**: Use the current config with `unsafe-eval` for easier development
2. **Production**: Use the secure config with nonces
3. **Testing**: Test thoroughly in staging with production CSP settings
4. **Monitoring**: Monitor CSP violation reports in production

## Next Steps

1. Test the current configuration
2. If it works, consider migrating to the secure version for production
3. Set up CSP violation reporting for production monitoring
4. Review and update CSP policies regularly