'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactNode, useState, useEffect } from 'react'

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

  const [showDevtools, setShowDevtools] = useState(false)

  useEffect(() => {
    // Only show devtools in development and after hydration
    if (process.env.NODE_ENV === 'development') {
      setShowDevtools(true)
    }
  }, [])

  return (
    <QueryClientProvider client={client}>
      {children}
      {showDevtools && (
        <div style={{ display: 'none' }}>
          {/* Devtools will be loaded dynamically on the client */}
        </div>
      )}
    </QueryClientProvider>
  )
} 