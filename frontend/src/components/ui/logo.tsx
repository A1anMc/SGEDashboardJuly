import React from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';

interface LogoProps {
  variant?: 'full' | 'icon';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  href?: string;
}

export const Logo: React.FC<LogoProps> = ({ 
  variant = 'full', 
  size = 'md', 
  className,
  href = '/'
}) => {
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };

  const textSizes = {
    sm: 'text-lg',
    md: 'text-xl',
    lg: 'text-2xl'
  };

  const LogoContent = () => (
    <div className={cn('flex items-center space-x-3 transition-all duration-300 hover:scale-105', className)}>
      <div className="relative group">
        <img 
          src="/icon.svg" 
          alt="NavImpact" 
          className={cn(
            sizeClasses[size],
            'transition-all duration-300 group-hover:rotate-12 group-hover:scale-110'
          )} 
        />
        {/* Subtle glow effect on hover */}
        <div className="absolute inset-0 rounded-full bg-energy-coral/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      </div>
      
      {variant === 'full' && (
        <span className={cn('font-bold transition-all duration-300', textSizes[size])}>
          <span className="text-impact-teal group-hover:text-impact-teal/80 transition-colors duration-300">Nav</span>
          <span className="text-energy-coral group-hover:text-energy-coral/80 transition-colors duration-300">Impact</span>
        </span>
      )}
    </div>
  );

  if (href) {
    return (
      <Link href={href} className="group">
        <LogoContent />
      </Link>
    );
  }

  return <LogoContent />;
};

export default Logo; 