# SGE Dashboard Frontend

Modern, responsive frontend for the Shadow Goose Entertainment Grant Management Dashboard built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

### In Development 🚧
- 🎨 Modern UI with Tailwind CSS and Headless UI
- 📱 Responsive dashboard layout
- 🔄 Server state management with React Query
- 🚀 Fast refresh with Turbopack
- 🔔 Toast notifications
- 🏃 Quick actions menu
- 📊 Grant statistics dashboard

### Planned Features 📋
- 📈 Interactive data visualization with Recharts
- 🔍 Advanced grant search and filtering
- 📋 Dynamic tables with TanStack Table
- 🌙 Dark/light mode support
- 📱 Mobile-optimized views
- 📊 Analytics dashboard
- 🔒 User authentication

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Build Tool**: Turbopack
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: Headless UI
- **State Management**: React Query
- **API Client**: Axios
- **Notifications**: React Hot Toast
- **Data Visualization**: Recharts (planned)
- **Tables**: TanStack Table (planned)

## Getting Started

### Prerequisites

- Node.js 18 or higher
- npm or yarn
- Backend API running (see main README)

### Installation

1. **Navigate to the frontend directory**

```bash
cd frontend
```

2. **Install dependencies**

```bash
npm install
# or
yarn install
```

3. **Set up environment variables**

Create a `.env.local` file:

```env
# Required
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_DEBUG_MODE=true
```

4. **Start the development server**

```bash
npm run dev
# or
yarn dev
```

The application will be available at [http://localhost:3000](http://localhost:3000).

## Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js 14 App Router
│   │   ├── (auth)/         # Authentication routes
│   │   ├── (dashboard)/    # Dashboard routes
│   │   ├── layout.tsx      # Root layout
│   │   └── page.tsx        # Home page
│   ├── components/
│   │   ├── common/         # Shared components
│   │   │   ├── Button/
│   │   │   ├── Card/
│   │   │   └── Input/
│   │   ├── dashboard/      # Dashboard components
│   │   │   ├── Stats/
│   │   │   └── Charts/
│   │   ├── grants/         # Grant management
│   │   │   ├── GrantList/
│   │   │   └── GrantForm/
│   │   └── layout/         # Layout components
│   │       ├── Header/
│   │       └── Sidebar/
│   ├── hooks/              # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useGrants.ts
│   │   └── useToast.ts
│   ├── lib/                # Utilities
│   │   ├── api.ts         # API client
│   │   └── utils.ts       # Helper functions
│   ├── services/           # API services
│   │   ├── auth.ts
│   │   └── grants.ts
│   ├── styles/             # Global styles
│   │   └── globals.css
│   └── types/              # TypeScript types
│       ├── api.ts
│       └── models.ts
├── public/                 # Static assets
└── tests/                  # Test files
    ├── components/
    ├── hooks/
    └── utils/
```

## Development

### Available Scripts

```bash
# Development
npm run dev         # Start development server
npm run lint        # Run ESLint
npm run lint:fix    # Fix ESLint errors
npm run format      # Format with Prettier
npm run typecheck   # Run TypeScript checks

# Testing
npm run test        # Run Jest tests
npm run test:watch  # Run tests in watch mode
npm run test:ci     # Run tests in CI mode

# Production
npm run build       # Build for production
npm start          # Start production server
```

### Code Style

- Use TypeScript for all new code
- Follow functional component patterns
- Implement proper loading states
- Handle errors gracefully
- Add JSDoc comments for complex logic
- Use CSS modules or Tailwind for styling

Example component:

```tsx
import { FC } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getGrants } from '@/services/grants';

interface GrantListProps {
  status?: 'open' | 'closed';
  onSelect: (id: string) => void;
}

export const GrantList: FC<GrantListProps> = ({ status, onSelect }) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['grants', status],
    queryFn: () => getGrants({ status })
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div className="space-y-4">
      {data.map((grant) => (
        <div
          key={grant.id}
          onClick={() => onSelect(grant.id)}
          className="p-4 hover:bg-gray-50 cursor-pointer"
        >
          <h3>{grant.title}</h3>
          <p>{grant.description}</p>
        </div>
      ))}
    </div>
  );
};
```

### API Integration

The frontend uses React Query for API integration:

```tsx
// Example API hook
export const useGrants = (filters: GrantFilters) => {
  return useQuery({
    queryKey: ['grants', filters],
    queryFn: () => getGrants(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
```

### State Management

- Use React Query for server state
- Use React Context for global UI state
- Use local state for component-specific state

## Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Run all checks:
   ```bash
   npm run lint
   npm run typecheck
   npm run test
   ```
4. Submit a pull request

### Pull Request Guidelines

- Include screenshots for UI changes
- Add tests for new features
- Update documentation
- Follow existing code style
- Keep changes focused and atomic

## License

This project is proprietary and confidential.
© 2024 Shadow Goose Entertainment
# Cache clear trigger
