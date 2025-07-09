# Error Handling Guidelines

## Overview

The SGE Dashboard implements a standardized error handling system. All new code contributions must follow these guidelines to maintain consistency and reliability.

## Frontend Guidelines

### 1. Component Error Handling

Always wrap component trees with ErrorBoundary:

```tsx
import { ErrorBoundary } from '../components/ui/error-boundary';

function MyFeature() {
  return (
    <ErrorBoundary>
      <MyComponent />
    </ErrorBoundary>
  );
}
```

### 2. API Error Handling

Use the error handling utilities for API calls:

```tsx
import { handleApiError, getErrorMessage } from '../utils/error-handling';

// In React Query
const { data, error } = useQuery({
  queryKey: ['data'],
  queryFn: async () => {
    try {
      const response = await api.get('/data');
      return response.data;
    } catch (error) {
      handleApiError(error, 'Failed to fetch data');
      throw error;
    }
  },
});

// Show errors to users
if (error) {
  return <ErrorAlert message={getErrorMessage(error)} />;
}
```

### 3. Form Validation

Handle validation errors properly:

```tsx
import { getValidationErrors } from '../utils/error-handling';

function MyForm() {
  const handleSubmit = async (data) => {
    try {
      await api.post('/data', data);
    } catch (error) {
      const validationErrors = getValidationErrors(error);
      // Handle validation errors
    }
  };
}
```

### 4. Retry Logic

Implement retry logic for transient failures:

```tsx
import { shouldRetry, getRetryDelay } from '../utils/error-handling';

async function fetchWithRetry() {
  let retryCount = 0;
  while (true) {
    try {
      return await api.get('/data');
    } catch (error) {
      if (!shouldRetry(error, retryCount)) throw error;
      await new Promise(resolve => setTimeout(resolve, getRetryDelay(retryCount)));
      retryCount++;
    }
  }
}
```

## Backend Guidelines

### 1. Error Response Format

All API endpoints must return errors in the standard format:

```python
from fastapi import HTTPException

def my_endpoint():
    try:
        # Your logic here
        pass
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "message": str(e),
                "error_code": "VALIDATION_ERROR",
                "details": {...}
            }
        )
```

### 2. Error Categories

Use appropriate HTTP status codes:

- 400: Bad Request (validation errors)
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Unprocessable Entity (business logic errors)
- 500: Internal Server Error

### 3. Error Logging

Always log errors with proper context:

```python
import logging

logger = logging.getLogger(__name__)

try:
    # Your logic here
    pass
except Exception as e:
    logger.error("Operation failed", exc_info=e, extra={
        "context": "relevant_context",
        "user_id": user_id
    })
```

## Testing Guidelines

### 1. Error Test Cases

Include error test cases in your tests:

```typescript
describe('MyComponent', () => {
  it('handles API errors', async () => {
    // Mock API error
    api.get.mockRejectedValue(new Error('API Error'));
    
    render(<MyComponent />);
    
    // Verify error handling
    expect(screen.getByText('Error message')).toBeInTheDocument();
  });
});
```

### 2. Error Boundary Tests

Test error boundaries:

```typescript
describe('ErrorBoundary', () => {
  it('catches and handles errors', () => {
    const ThrowError = () => {
      throw new Error('Test Error');
    };
    
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });
});
```

## Documentation

1. Document error handling in your code:
   - Use JSDoc comments for functions
   - Explain error scenarios
   - Provide examples

2. Update relevant documentation:
   - API documentation
   - Component documentation
   - Error handling architecture docs

## Review Checklist

Before submitting a PR, ensure:

- [ ] Error boundaries are used appropriately
- [ ] API errors are handled using utilities
- [ ] Validation errors are handled properly
- [ ] Error messages are user-friendly
- [ ] Errors are logged with context
- [ ] Error handling is tested
- [ ] Documentation is updated

For more details, see the [Error Handling Architecture](./architecture/error-handling.md) documentation. 