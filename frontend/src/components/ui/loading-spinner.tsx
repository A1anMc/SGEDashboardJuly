import React from 'react';
import { cn } from '@/lib/utils';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  variant?: 'default' | 'brand';
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  className,
  variant = 'default'
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8'
  };

  const colors = variant === 'brand' 
    ? 'border-impact-teal/20 border-t-impact-teal' 
    : 'border-gray-200 border-t-gray-600';

  return (
    <div
      className={cn(
        'animate-spin rounded-full border-2 border-solid',
        sizeClasses[size],
        colors,
        className
      )}
    />
  );
};

export default LoadingSpinner; 