'use client';

import React from 'react';
import { XCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from './button';

interface ErrorAlertProps {
  title?: string;
  message: string;
  retryable?: boolean;
  onRetry?: () => void;
  onDismiss?: () => void;
  details?: string[];
  severity?: 'error' | 'warning';
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({
  title,
  message,
  retryable = false,
  onRetry,
  onDismiss,
  details = [],
  severity = 'error'
}) => {
  const [isExpanded, setIsExpanded] = React.useState(false);

  const bgColor = severity === 'error' ? 'bg-red-50' : 'bg-yellow-50';
  const borderColor = severity === 'error' ? 'border-red-400' : 'border-yellow-400';
  const textColor = severity === 'error' ? 'text-red-800' : 'text-yellow-800';
  const iconColor = severity === 'error' ? 'text-red-400' : 'text-yellow-400';

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className={`rounded-md ${bgColor} p-4 border ${borderColor}`}
      >
        <div className="flex items-start">
          <div className="flex-shrink-0">
            {severity === 'error' ? (
              <XCircle className={`h-5 w-5 ${iconColor}`} />
            ) : (
              <AlertCircle className={`h-5 w-5 ${iconColor}`} />
            )}
          </div>
          <div className="ml-3 flex-1">
            {title && (
              <h3 className={`text-sm font-medium ${textColor}`}>
                {title}
              </h3>
            )}
            <div className={`text-sm ${textColor} mt-1`}>
              {message}
            </div>
            
            {details.length > 0 && (
              <div className="mt-2">
                <button
                  type="button"
                  onClick={() => setIsExpanded(!isExpanded)}
                  className={`text-sm ${textColor} underline focus:outline-none`}
                >
                  {isExpanded ? 'Hide details' : 'Show details'}
                </button>
                
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="mt-2 space-y-1"
                    >
                      {details.map((detail, index) => (
                        <p key={index} className={`text-sm ${textColor}`}>
                          • {detail}
                        </p>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )}
            
            {(retryable || onDismiss) && (
              <div className="mt-4 flex space-x-3">
                {retryable && onRetry && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={onRetry}
                    className="flex items-center"
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Retry
                  </Button>
                )}
                {onDismiss && (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={onDismiss}
                  >
                    Dismiss
                  </Button>
                )}
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}; 