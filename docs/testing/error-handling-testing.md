# Error Handling Testing Guide

This guide covers testing strategies for error handling across the SGE Dashboard, including API failures, component error boundaries, and retry behavior.

## Setting Up Test Environment

### 1. MSW (Mock Service Worker) Setup

```typescript
// src/mocks/handlers.ts
import { rest } from 'msw';

export const handlers = [
  // Mock successful response
  rest.get('/api/data', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({ data: 'test' })
    );
  }),

  // Mock error response
  rest.get('/api/error', (req, res, ctx) => {
    return res(
      ctx.status(500),
      ctx.json({
        message: 'Internal Server Error',
        error_code: 'SERVER_ERROR'
      })
    );
  }),

  // Mock validation error
  rest.post('/api/validate', (req, res, ctx) => {
    return res(
      ctx.status(400),
      ctx.json({
        message: 'Validation Error',
        error_code: 'VALIDATION_ERROR',
        details: [
          {
            loc: 'email',
            msg: 'Invalid email format',
            type: 'value_error'
          }
        ]
      })
    );
  }),

  // Mock network error
  rest.get('/api/timeout', (req, res, ctx) => {
    return res.networkError('Failed to connect');
  }),

  // Mock retry scenario
  rest.get('/api/retry', (req, res, ctx) => {
    const attempt = sessionStorage.getItem('retryAttempt') || '0';
    const currentAttempt = parseInt(attempt);
    
    if (currentAttempt < 2) {
      sessionStorage.setItem('retryAttempt', (currentAttempt + 1).toString());
      return res.networkError('Temporary failure');
    }
    
    sessionStorage.removeItem('retryAttempt');
    return res(
      ctx.status(200),
      ctx.json({ data: 'success after retry' })
    );
  })
];
```

### 2. Supabase API Mocking

```typescript
// src/mocks/supabase.ts
import { createClient } from '@supabase/supabase-js';

export const mockSupabaseClient = {
  from: (table: string) => ({
    select: jest.fn().mockImplementation(() => ({
      eq: jest.fn().mockImplementation(() => ({
        single: jest.fn().mockResolvedValue({ data: null, error: { message: 'Not found' } }),
        data: null,
        error: { message: 'Not found' }
      }))
    })),
    insert: jest.fn().mockImplementation(() => ({
      select: jest.fn().mockResolvedValue({ 
        data: null, 
        error: { 
          message: 'Database error',
          code: 'DB_ERROR' 
        } 
      })
    }))
  }),
  auth: {
    signIn: jest.fn().mockRejectedValue(new Error('Auth error')),
    signOut: jest.fn().mockResolvedValue(null)
  }
};
```

## Testing Error Boundaries

### 1. Basic Error Boundary Tests

```typescript
// src/components/__tests__/ErrorBoundary.test.tsx
import { render, screen } from '@testing-library/react';
import { ErrorBoundary } from '../ErrorBoundary';

describe('ErrorBoundary', () => {
  // Suppress console.error for expected errors
  const originalError = console.error;
  beforeAll(() => {
    console.error = jest.fn();
  });
  afterAll(() => {
    console.error = originalError;
  });

  it('renders children when no error occurs', () => {
    render(
      <ErrorBoundary>
        <div>Normal content</div>
      </ErrorBoundary>
    );
    expect(screen.getByText('Normal content')).toBeInTheDocument();
  });

  it('renders fallback UI when error occurs', () => {
    const ThrowError = () => {
      throw new Error('Test error');
    };

    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('renders custom fallback when provided', () => {
    const ThrowError = () => {
      throw new Error('Test error');
    };

    render(
      <ErrorBoundary
        fallback={<div>Custom error message</div>}
      >
        <ThrowError />
      </ErrorBoundary>
    );

    expect(screen.getByText('Custom error message')).toBeInTheDocument();
  });
});
```

### 2. Testing Error Recovery

```typescript
// src/components/__tests__/ErrorRecovery.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ErrorBoundary } from '../ErrorBoundary';

describe('ErrorBoundary Recovery', () => {
  it('allows retry after error', () => {
    let shouldThrow = true;
    
    const MaybeThrow = () => {
      if (shouldThrow) {
        throw new Error('Test error');
      }
      return <div>Recovered content</div>;
    };

    const { rerender } = render(
      <ErrorBoundary>
        <MaybeThrow />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    
    shouldThrow = false;
    fireEvent.click(screen.getByText('Reload Page'));
    
    rerender(
      <ErrorBoundary>
        <MaybeThrow />
      </ErrorBoundary>
    );

    expect(screen.getByText('Recovered content')).toBeInTheDocument();
  });
});
```

## Testing API Error Handling

### 1. Testing Error Responses

```typescript
// src/services/__tests__/api.test.ts
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DataComponent } from '../DataComponent';

const server = setupServer(
  rest.get('/api/data', (req, res, ctx) => {
    return res(
      ctx.status(500),
      ctx.json({
        message: 'Server error',
        error_code: 'INTERNAL_ERROR'
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false
    }
  }
});

describe('API Error Handling', () => {
  it('handles server errors', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <DataComponent />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Server error')).toBeInTheDocument();
    });
  });
});
```

### 2. Testing Retry Logic

```typescript
// src/services/__tests__/retry.test.ts
import { fetchWithRetry } from '../api';
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer();

describe('Retry Logic', () => {
  it('retries failed requests with backoff', async () => {
    let attempts = 0;
    
    server.use(
      rest.get('/api/test', (req, res, ctx) => {
        attempts++;
        if (attempts < 3) {
          return res.networkError('Temporary failure');
        }
        return res(ctx.json({ success: true }));
      })
    );

    const result = await fetchWithRetry('/api/test');
    expect(attempts).toBe(3);
    expect(result.success).toBe(true);
  });

  it('gives up after max retries', async () => {
    server.use(
      rest.get('/api/test', (req, res) => {
        return res.networkError('Persistent failure');
      })
    );

    await expect(fetchWithRetry('/api/test')).rejects.toThrow();
  });
});
```

## Testing Validation Errors

```typescript
// src/components/__tests__/Form.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { Form } from '../Form';

const server = setupServer(
  rest.post('/api/submit', (req, res, ctx) => {
    return res(
      ctx.status(400),
      ctx.json({
        message: 'Validation failed',
        error_code: 'VALIDATION_ERROR',
        details: [
          {
            loc: 'email',
            msg: 'Invalid email',
            type: 'value_error'
          }
        ]
      })
    );
  })
);

describe('Form Validation', () => {
  it('displays validation errors', async () => {
    render(<Form />);
    
    fireEvent.click(screen.getByText('Submit'));
    
    await waitFor(() => {
      expect(screen.getByText('Invalid email')).toBeInTheDocument();
    });
  });
});
```

## Testing Error States in Components

```typescript
// src/components/__tests__/ErrorStates.test.tsx
import { render, screen } from '@testing-library/react';
import { LoadingState } from '../LoadingState';
import { ErrorState } from '../ErrorState';
import { EmptyState } from '../EmptyState';

describe('Component Error States', () => {
  it('shows loading state', () => {
    render(<LoadingState />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('shows error state', () => {
    const error = new Error('Test error');
    render(<ErrorState error={error} onRetry={() => {}} />);
    expect(screen.getByText('Test error')).toBeInTheDocument();
  });

  it('shows empty state', () => {
    render(<EmptyState message="No data found" />);
    expect(screen.getByText('No data found')).toBeInTheDocument();
  });
});
```

## Best Practices

1. **Isolation**: Test error handling in isolation using MSW or mock implementations
2. **Coverage**: Test both successful and error paths
3. **Retry Logic**: Verify retry behavior with different failure scenarios
4. **User Experience**: Test error messages and recovery options
5. **Edge Cases**: Include tests for timeout, network errors, and validation failures
6. **State Management**: Verify error state management in components
7. **Integration**: Test error handling across component boundaries

## Common Testing Scenarios Checklist

- [ ] API error responses (400, 401, 403, 404, 500)
- [ ] Network failures and timeouts
- [ ] Validation error handling
- [ ] Retry logic with backoff
- [ ] Error boundary fallback UI
- [ ] Error recovery flows
- [ ] Loading and empty states
- [ ] Error message display
- [ ] Error logging and monitoring
- [ ] State management during errors 