'use client';

import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cn } from '../../lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean;
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'default', asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button';
    return (
      <Comp
        className={cn(
          'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background',
          {
            'bg-gradient-to-r from-energy-coral to-energy-coral/90 text-white hover:from-energy-coral/90 hover:to-energy-coral shadow-lg hover:shadow-xl transition-all duration-300': variant === 'default',
            'bg-gradient-to-r from-soft-crimson to-soft-crimson/90 text-white hover:from-soft-crimson/90 hover:to-soft-crimson shadow-lg hover:shadow-xl transition-all duration-300': variant === 'destructive',
            'border border-cool-gray hover:bg-gradient-to-r hover:from-mist-white hover:to-gray-50 hover:text-gray-900 hover:shadow-md transition-all duration-300': variant === 'outline',
            'bg-gradient-to-r from-impact-teal to-impact-teal/90 text-white hover:from-impact-teal/90 hover:to-impact-teal shadow-lg hover:shadow-xl transition-all duration-300': variant === 'secondary',
            'hover:bg-accent hover:text-accent-foreground': variant === 'ghost',
            'underline-offset-4 hover:underline text-primary': variant === 'link',
            'h-10 py-2 px-4': size === 'default',
            'h-9 px-3': size === 'sm',
            'h-11 px-8': size === 'lg',
            'h-10 w-10': size === 'icon',
          },
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = 'Button';

export { Button }; 