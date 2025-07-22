import React from 'react';
import { cn } from '@/lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined';
  hover?: boolean;
}

export const Card: React.FC<CardProps> = ({ 
  className, 
  variant = 'default',
  hover = false,
  children,
  ...props 
}) => {
  const baseClasses = 'rounded-lg transition-all duration-300';
  
  const variantClasses = {
    default: 'bg-white shadow-sm border border-cool-gray/50',
    elevated: 'bg-white shadow-lg border border-cool-gray/30',
    outlined: 'bg-white border-2 border-cool-gray/30'
  };

  const hoverClasses = hover 
    ? 'hover:shadow-xl hover:border-impact-teal/20 hover:scale-[1.02]' 
    : '';

  return (
    <div
      className={cn(
        baseClasses,
        variantClasses[variant],
        hoverClasses,
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ 
  className, 
  children,
  ...props 
}) => (
  <div
    className={cn('flex flex-col space-y-1.5 p-6', className)}
    {...props}
  >
    {children}
  </div>
);

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({ 
  className, 
  children,
  ...props 
}) => (
  <h3
    className={cn('text-lg font-semibold leading-none tracking-tight text-gray-900', className)}
    {...props}
  >
    {children}
  </h3>
);

export const CardDescription: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({ 
  className, 
  children,
  ...props 
}) => (
  <p
    className={cn('text-sm text-gray-600', className)}
    {...props}
  >
    {children}
  </p>
);

export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ 
  className, 
  children,
  ...props 
}) => (
  <div className={cn('p-6 pt-0', className)} {...props}>
    {children}
  </div>
);

export const CardFooter: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ 
  className, 
  children,
  ...props 
}) => (
  <div className={cn('flex items-center p-6 pt-0', className)} {...props}>
    {children}
  </div>
); 