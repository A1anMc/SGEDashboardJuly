'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactNode, useState } from 'react'
import dynamic from 'next/dynamic'

// Dynamic import for ReactQueryDevtools (development only)
const ReactQueryDevtools = dynamic(
  () => import('@tanstack/react-query-devtools').then(mod => ({ default: mod.ReactQueryDevtools })),
  {
    ssr: false,
  }
)

export default function QueryProvider({ children }: { children: ReactNode }) {
  const [client] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        // Increase stale time to reduce unnecessary requests
        staleTime: 5 * 60 * 1000, // 5 minutes
        // Reduce cache time to ensure fresh data
        gcTime: 10 * 60 * 1000, // 10 minutes (was cacheTime)
        // Retry failed requests
        retry: 3,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
        // Refetch on window focus
        refetchOnWindowFocus: false,
        // Refetch on reconnect
        refetchOnReconnect: true,
        // Enable background refetching
        refetchOnMount: true,
      },
      mutations: {
        // Retry failed mutations
        retry: 1,
        retryDelay: 1000,
      },
    },
  }))

  return (
    <QueryClientProvider client={client}>
      {children}
      {process.env.NODE_ENV === 'development' && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  )
} 