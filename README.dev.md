# Error Handling

## Overview

The SGE Dashboard implements a comprehensive error handling system. This guide provides examples of how to use the error handling components and utilities in your code.

## Error Boundary

Use ErrorBoundary to catch and handle React component errors:

```tsx
import { ErrorBoundary } from '../components/ui/error-boundary';

function MyComponent() {
  return (
    <ErrorBoundary>
      <ComponentThatMightError />
    </ErrorBoundary>
  );
}

// With custom fallback
function MyComponentWithCustomFallback() {
  return (
    <ErrorBoundary
      fallback={
        <div className="text-red-500">
          Custom error message
        </div>
      }
    >
      <ComponentThatMightError />
    </ErrorBoundary>
  );
}
```

## Error Alert

Use ErrorAlert to display user-friendly error messages:

```tsx
import { ErrorAlert } from '../components/ui/error-alert';

function MyComponent() {
  return (
    <ErrorAlert
      title="Failed to load data"
      message="Please try again later"
      onDismiss={() => console.log('Alert dismissed')}
      action={{
        label: 'Retry',
        onClick: () => handleRetry(),
      }}
    />
  );
}
```

## API Error Handling

Handle API errors using the error utilities:

```tsx
import { handleApiError, getErrorMessage } from '../utils/error-handling';
import { useQuery, useMutation } from '@tanstack/react-query';

// In a component
function MyComponent() {
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

  const mutation = useMutation({
    mutationFn: (data) => api.post('/data', data),
    onError: (error) => {
      handleApiError(error, 'Failed to save data');
    },
  });

  if (error) {
    return (
      <ErrorAlert
        title="Error"
        message={getErrorMessage(error)}
      />
    );
  }

  return <div>{/* Your component JSX */}</div>;
}
```

## Validation Errors

Handle validation errors from the API:

```tsx
import { getValidationErrors } from '../utils/error-handling';

function MyForm() {
  const [errors, setErrors] = useState<ValidationError[]>([]);

  const handleSubmit = async (data) => {
    try {
      await api.post('/data', data);
    } catch (error) {
      const validationErrors = getValidationErrors(error);
      if (validationErrors.length > 0) {
        setErrors(validationErrors);
      }
    }
  };

  return (
    <form>
      {errors.map((error) => (
        <div key={error.loc} className="text-red-500">
          {error.msg}
        </div>
      ))}
      {/* Form fields */}
    </form>
  );
}
```

## Retry Logic

Use retry logic for transient failures:

```tsx
import { shouldRetry, getRetryDelay } from '../utils/error-handling';

async function fetchWithRetry(url: string) {
  let retryCount = 0;

  while (true) {
    try {
      const response = await fetch(url);
      return response;
    } catch (error) {
      if (!shouldRetry(error, retryCount)) {
        throw error;
      }

      const delay = getRetryDelay(retryCount);
      await new Promise(resolve => setTimeout(resolve, delay));
      retryCount++;
    }
  }
}
```

## Best Practices

1. Always wrap component trees with ErrorBoundary
2. Use ErrorAlert for user-facing errors
3. Handle API errors with handleApiError
4. Implement retry logic for network requests
5. Log errors with proper context
6. Use validation error handling for forms
7. Provide clear error messages to users

For more detailed information about the error handling architecture, see [Error Handling Architecture](docs/architecture/error-handling.md). 