'use client';

import * as React from 'react';
import { Listbox } from '@headlessui/react';
import { cn } from '@/lib/utils';

const Select = Listbox;
const SelectTrigger = Listbox.Button;
const SelectValue = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, children, ...props }, ref) => (
  <div ref={ref} className={cn('truncate', className)} {...props}>
    {children}
  </div>
));
SelectValue.displayName = 'SelectValue';

const SelectContent = React.forwardRef<
  HTMLUListElement,
  React.ComponentPropsWithoutRef<typeof Listbox.Options>
>(({ className, children, ...props }, ref) => (
  <Listbox.Options
    ref={ref}
    className={cn(
      'relative z-50 min-w-[8rem] overflow-hidden rounded-md border bg-white text-gray-700 shadow-md',
      className
    )}
    {...props}
  >
    {children}
  </Listbox.Options>
));
SelectContent.displayName = 'SelectContent';

const SelectItem = React.forwardRef<
  HTMLLIElement,
  React.ComponentPropsWithoutRef<typeof Listbox.Option>
>(({ className, children, ...props }, ref) => (
  <Listbox.Option
    ref={ref}
    className={cn(
      'relative flex w-full cursor-default select-none items-center py-2 pl-8 pr-2 text-sm outline-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 hover:bg-gray-100',
      className
    )}
    {...props}
  >
    {children}
  </Listbox.Option>
));
SelectItem.displayName = 'SelectItem';

export { Select, SelectTrigger, SelectValue, SelectContent, SelectItem }; 