import React from 'react';
import { cn } from '@/lib/utils';

interface AvatarProps {
  email?: string;
  name?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  fallback?: string;
}

export const Avatar: React.FC<AvatarProps> = ({
  email,
  name,
  size = 'md',
  className,
  fallback
}) => {
  // Generate seed from email or name
  const seed = email || name || 'default';
  
  // Dicebear avatar URL with different styles
  const avatarUrl = `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(seed)}&backgroundColor=b6e3f4,c0aede,d1d4f9,ffd5dc,ffdfbf`;
  
  // Size classes
  const sizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-10 w-10',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16'
  };

  // Fallback initials
  const getInitials = () => {
    if (name) {
      return name
        .split(' ')
        .map(word => word.charAt(0))
        .join('')
        .toUpperCase()
        .slice(0, 2);
    }
    if (email) {
      return email.charAt(0).toUpperCase();
    }
    return fallback || 'U';
  };

  return (
    <div className={cn('relative inline-block', className)}>
      <img
        src={avatarUrl}
        alt={`Avatar for ${name || email || 'user'}`}
        className={cn(
          'rounded-full object-cover border-2 border-gray-200',
          sizeClasses[size]
        )}
        onError={(e) => {
          // Fallback to initials if image fails to load
          const target = e.target as HTMLImageElement;
          target.style.display = 'none';
          const fallbackDiv = target.nextElementSibling as HTMLElement;
          if (fallbackDiv) {
            fallbackDiv.style.display = 'flex';
          }
        }}
      />
      {/* Fallback initials */}
      <div
        className={cn(
          'absolute inset-0 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold',
          sizeClasses[size],
          'text-xs'
        )}
        style={{ display: 'none' }}
      >
        {getInitials()}
      </div>
    </div>
  );
};

export default Avatar; 