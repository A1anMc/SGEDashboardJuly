/**
 * Error Handling Utilities
 * 
 * This module provides a comprehensive set of utilities for handling errors
 * in a consistent way across the application. It includes functions for
 * error type checking, message extraction, validation error handling,
 * and retry logic.
 * 
 * @module error-handling
 */

import { AxiosError } from 'axios';
import { toast } from 'react-hot-toast';

/**
 * Standard error response from the API
 * @interface StandardError
 * @property {string} message - Human-readable error message
 * @property {number} status_code - HTTP status code
 * @property {string} [error_code] - Optional error code for specific error types
 * @property {any} [details] - Additional error details
 * @property {string} [timestamp] - When the error occurred
 */
export interface StandardError {
  message: string;
  status_code: number;
  error_code?: string;
  details?: any;
  timestamp?: string;
}

/**
 * Validation error structure from the API
 * @interface ValidationError
 * @property {string} loc - Location of the validation error (field name)
 * @property {string} msg - Error message
 * @property {string} type - Type of validation error
 */
export interface ValidationError {
  loc: string;
  msg: string;
  type: string;
}

/**
 * Type guard to check if an error is a StandardError
 * @param {any} error - The error to check
 * @returns {boolean} True if the error is a StandardError
 * 
 * @example
 * if (isStandardError(error)) {
 *   console.log(error.message);
 * }
 */
export function isStandardError(error: any): error is StandardError {
  return (
    error &&
    typeof error === 'object' &&
    'message' in error &&
    'status_code' in error
  );
}

/**
 * Type guard to check if an error is a ValidationError
 * @param {any} error - The error to check
 * @returns {boolean} True if the error is a ValidationError
 * 
 * @example
 * if (isValidationError(error)) {
 *   console.log(error.msg);
 * }
 */
export function isValidationError(error: any): error is ValidationError {
  return (
    error &&
    typeof error === 'object' &&
    'loc' in error &&
    'msg' in error &&
    'type' in error
  );
}

/**
 * Extracts a human-readable error message from any error object
 * @param {unknown} error - The error to process
 * @returns {string} A human-readable error message
 * 
 * @example
 * const message = getErrorMessage(error);
 * console.log(message); // "Failed to fetch data"
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const data = error.response?.data;
    
    if (isStandardError(data)) {
      return data.message;
    }
    
    return error.message;
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
}

/**
 * Extracts validation errors from an error object
 * @param {unknown} error - The error to process
 * @returns {ValidationError[]} Array of validation errors
 * 
 * @example
 * const validationErrors = getValidationErrors(error);
 * validationErrors.forEach(err => {
 *   console.log(`${err.loc}: ${err.msg}`);
 * });
 */
export function getValidationErrors(error: unknown): ValidationError[] {
  if (error instanceof AxiosError) {
    const data = error.response?.data;
    
    if (isStandardError(data) && Array.isArray(data.details)) {
      return data.details;
    }
  }
  
  return [];
}

/**
 * Handles API errors by showing appropriate toast notifications
 * @param {unknown} error - The error to handle
 * @param {string} [context] - Optional context for the error message
 * 
 * @example
 * try {
 *   await api.get('/data');
 * } catch (error) {
 *   handleApiError(error, 'Failed to fetch data');
 * }
 */
export function handleApiError(error: unknown, context?: string): void {
  const message = getErrorMessage(error);
  const validationErrors = getValidationErrors(error);
  
  if (validationErrors.length > 0) {
    // Show validation errors
    validationErrors.forEach((err) => {
      toast.error(`${err.loc}: ${err.msg}`);
    });
  } else {
    // Show general error
    toast.error(context ? `${context}: ${message}` : message);
  }
  
  // Log error for debugging
  console.error('API Error:', {
    message,
    validationErrors,
    error,
  });
}

/**
 * Gets the HTTP status code from an error
 * @param {unknown} error - The error to process
 * @returns {number} The HTTP status code or 500 if not found
 */
export function getErrorStatusCode(error: unknown): number {
  if (error instanceof AxiosError) {
    return error.response?.status || 500;
  }
  return 500;
}

/**
 * Checks if an error is a 404 Not Found error
 * @param {unknown} error - The error to check
 * @returns {boolean} True if the error is a 404
 */
export function isNotFoundError(error: unknown): boolean {
  return getErrorStatusCode(error) === 404;
}

/**
 * Checks if an error is a 401 Unauthorized error
 * @param {unknown} error - The error to check
 * @returns {boolean} True if the error is a 401
 */
export function isUnauthorizedError(error: unknown): boolean {
  return getErrorStatusCode(error) === 401;
}

/**
 * Checks if an error is a 403 Forbidden error
 * @param {unknown} error - The error to check
 * @returns {boolean} True if the error is a 403
 */
export function isForbiddenError(error: unknown): boolean {
  return getErrorStatusCode(error) === 403;
}

/**
 * Checks if an error is a network error
 * @param {unknown} error - The error to check
 * @returns {boolean} True if the error is a network error
 */
export function isNetworkError(error: unknown): boolean {
  return error instanceof AxiosError && !error.response;
}

/**
 * Calculates the delay for retry attempts using exponential backoff with jitter
 * @param {number} retryCount - The current retry attempt number
 * @returns {number} The delay in milliseconds
 * 
 * @example
 * const delay = getRetryDelay(retryCount);
 * await new Promise(resolve => setTimeout(resolve, delay));
 */
export function getRetryDelay(retryCount: number): number {
  // Exponential backoff with jitter
  const baseDelay = 1000; // 1 second
  const maxDelay = 30000; // 30 seconds
  const exponentialDelay = Math.min(
    maxDelay,
    baseDelay * Math.pow(2, retryCount)
  );
  
  // Add random jitter (±20%)
  const jitter = exponentialDelay * 0.2 * (Math.random() * 2 - 1);
  return exponentialDelay + jitter;
}

/**
 * Determines if a failed request should be retried
 * @param {unknown} error - The error that occurred
 * @param {number} retryCount - The current retry attempt number
 * @returns {boolean} True if the request should be retried
 * 
 * @example
 * if (shouldRetry(error, retryCount)) {
 *   const delay = getRetryDelay(retryCount);
 *   await new Promise(resolve => setTimeout(resolve, delay));
 *   // Retry the request
 * }
 */
export function shouldRetry(error: unknown, retryCount: number): boolean {
  if (retryCount >= 3) return false; // Maximum 3 retries
  
  if (error instanceof AxiosError) {
    const status = error.response?.status;
    
    // Retry on network errors or specific status codes
    return (
      !error.response || // Network error
      status === 408 || // Request timeout
      status === 429 || // Too many requests
      (status !== undefined && status >= 500 && status <= 599) // Server errors
    );
  }
  
  return false;
} 