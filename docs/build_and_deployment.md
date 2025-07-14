# Build and Deployment Configuration

## Recent Build Issues and Fixes

### 1. Test Files in Production Build
**Issue:** Test files were being included in the production build, causing dependencies like `@testing-library/react` to be required in production.

**Fix:** Updated `frontend/tsconfig.json` to properly exclude test files:
```json
{
  "exclude": [
    "node_modules",
    "tests",
    "**/*.test.ts",
    "**/*.test.tsx",
    "**/__tests__/**"
  ]
}
```

### 2. React Query SSR Issues
**Issue:** Components using `useQueryClient()` were not wrapped in a `QueryClientProvider` during prerender/static export, causing build failures.

**Fix:** 
1. Created `frontend/src/components/QueryProvider.tsx`:
```tsx
'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactNode, useState } from 'react'

export default function QueryProvider({ children }: { children: ReactNode }) {
  const [client] = useState(() => new QueryClient())
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}
```

2. Integrated in `frontend/src/app/layout.tsx` using relative imports:
```tsx
import QueryProvider from '../components/QueryProvider'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full bg-gray-100">
      <body className="h-full">
        <QueryProvider>
          <DashboardLayout>{children}</DashboardLayout>
        </QueryProvider>
      </body>
    </html>
  );
}
```

## Current Project Structure

### Frontend
- **Framework:** Next.js 14.0.0
- **Key Dependencies:**
  - React Query for data fetching
  - Tailwind CSS for styling
  - TypeScript for type safety

### Development Commands
```bash
# Install dependencies
make install  # Runs pip install -r backend/requirements.txt and npm install in frontend

# Development
make frontend  # Runs npm run dev in frontend/
make backend   # Runs uvicorn app.main:app --reload in backend/
make dev       # Runs both backend & frontend in parallel

# Testing
make test     # Runs pytest in backend and npm run test in frontend

# Code Quality
make lint     # Runs ruff and pylint on backend and npm run lint in frontend
make format   # Runs black and isort on backend and npm run format in frontend

# Database
make db-reset # Resets PostgreSQL database by running alembic downgrade base then upgrade head
```

## Deployment Configuration

### Render Setup
- **Build Command:** `npm install && npm run build`
- **Node Version:** 22.16.0 (default)
- **Bun Version:** 1.1.0 (default)

### Important Notes
1. Use relative imports instead of `@/` path aliases in production code to ensure build compatibility
2. Test files must be properly excluded from production builds
3. React Query must be properly configured for SSR/static generation

## Git Workflow
- All changes must be tested locally before deployment
- GitHub pushes require explicit permission
- Build cache should be cleared on Render after significant dependency changes

## Current Functionality
- ✅ Server-side rendering working correctly
- ✅ React Query properly configured for SSR
- ✅ Test files excluded from production builds
- ✅ Development and production builds aligned
- ✅ All pages rendering correctly (/grants, /tasks, /admin/tags) 