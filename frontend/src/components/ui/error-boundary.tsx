/**
 * ErrorBoundary Component
 * 
 * A React error boundary component that catches JavaScript errors anywhere in its child
 * component tree and displays a fallback UI instead of the component tree that crashed.
 * 
 * Features:
 * - Catches and handles React component errors
 * - Provides a default fallback UI
 * - Supports custom fallback components
 * - Includes a reload option
 * - Logs errors for debugging
 * 
 * @example
 * // Basic usage
 * <ErrorBoundary>
 *   <MyComponent />
 * </ErrorBoundary>
 * 
 * @example
 * // With custom fallback
 * <ErrorBoundary
 *   fallback={<CustomErrorComponent />}
 * >
 *   <MyComponent />
 * </ErrorBoundary>
 */

import React from 'react';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

/**
 * Props for the ErrorBoundary component
 * @interface ErrorBoundaryProps
 * @property {React.ReactNode} children - Child components to be rendered
 * @property {React.ReactNode} [fallback] - Optional custom fallback component
 */
interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

/**
 * State for the ErrorBoundary component
 * @interface ErrorBoundaryState
 * @property {boolean} hasError - Whether an error has occurred
 * @property {Error | null} error - The error object if an error occurred
 */
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

/**
 * ErrorBoundary Class Component
 * 
 * @extends {React.Component<ErrorBoundaryProps, ErrorBoundaryState>}
 * 
 * Usage:
 * ```tsx
 * // Wrap components that might error
 * <ErrorBoundary>
 *   <ComponentThatMightError />
 * </ErrorBoundary>
 * 
 * // With custom fallback UI
 * <ErrorBoundary
 *   fallback={
 *     <div>Custom error message</div>
 *   }
 * >
 *   <ComponentThatMightError />
 * </ErrorBoundary>
 * ```
 */
export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  /**
   * Static method to update state when an error occurs
   * @param {Error} error - The error that was caught
   * @returns {ErrorBoundaryState} New state with error information
   */
  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  /**
   * Lifecycle method called when an error occurs
   * @param {Error} error - The error that was caught
   * @param {React.ErrorInfo} errorInfo - Additional error information
   */
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error to your error reporting service
    console.error('Component Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      // Return custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div className="flex flex-col items-center justify-center min-h-[200px] p-4 rounded-lg border border-red-200 bg-red-50">
          <ExclamationTriangleIcon className="w-12 h-12 text-red-500 mb-4" />
          <h3 className="text-lg font-semibold text-red-700 mb-2">
            Something went wrong
          </h3>
          <p className="text-sm text-red-600 text-center max-w-md">
            {this.state.error?.message || 'An unexpected error occurred'}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors"
          >
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 