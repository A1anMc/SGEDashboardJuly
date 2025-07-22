'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info';
  size?: 'sm' | 'md' | 'lg';
}

export const Badge: React.FC<BadgeProps> = ({ 
  className, 
  variant = 'default',
  size = 'md',
  children,
  ...props 
}) => {
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base'
  };

  const variantClasses = {
    default: 'bg-impact-teal/10 text-impact-teal border border-impact-teal/20',
    success: 'bg-mint-breeze/20 text-green-700 border border-mint-breeze/30',
    warning: 'bg-warm-amber/20 text-amber-700 border border-warm-amber/30',
    error: 'bg-soft-crimson/20 text-red-700 border border-soft-crimson/30',
    info: 'bg-energy-coral/10 text-energy-coral border border-energy-coral/20'
  };

  return (
    <div
      className={cn(
        'inline-flex items-center rounded-full font-medium transition-all duration-300 hover:scale-105',
        sizeClasses[size],
        variantClasses[variant],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export default Badge; 