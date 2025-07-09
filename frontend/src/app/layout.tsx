import { Toaster } from 'react-hot-toast';
import { ErrorBoundary } from '../components/ui/error-boundary';
import './globals.css';
import type { Metadata } from 'next';
import DashboardLayout from '../components/layout/DashboardLayout';
import QueryProvider from '../components/QueryProvider';

export const metadata: Metadata = {
  title: 'SGE Dashboard',
  description: 'Smart Grant Engine Dashboard',
};

// Custom SGE dashboard root layout, built by Alan – not boilerplate
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full bg-gray-100">
      <body className="h-full">
        <ErrorBoundary>
          <QueryProvider>
            <DashboardLayout>{children}</DashboardLayout>
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 5000,
                success: {
                  style: {
                    background: '#10B981',
                    color: 'white',
                  },
                },
                error: {
                  duration: 7000,
                  style: {
                    background: '#EF4444',
                    color: 'white',
                  },
                },
              }}
            />
          </QueryProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
