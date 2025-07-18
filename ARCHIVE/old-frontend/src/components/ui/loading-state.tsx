'use client';

import React from 'react';
import { Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

interface LoadingStateProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
  fullscreen?: boolean;
  transparent?: boolean;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading...',
  size = 'md',
  fullscreen = false,
  transparent = false
}) => {
  const containerClasses = [
    'flex flex-col items-center justify-center',
    fullscreen ? 'fixed inset-0 z-50' : 'p-8',
    !transparent && 'bg-white/80 backdrop-blur-sm'
  ].filter(Boolean).join(' ');

  const spinnerSizes = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };

  const textSizes = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };

  return (
    <div className={containerClasses}>
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex flex-col items-center space-y-4"
      >
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        >
          <Loader2 className={`${spinnerSizes[size]} text-primary animate-spin`} />
        </motion.div>
        
        {message && (
          <motion.p
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className={`${textSizes[size]} text-gray-600 text-center`}
          >
            {message}
          </motion.p>
        )}
      </motion.div>
    </div>
  );
}; 