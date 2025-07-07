import './globals.css';
import type { Metadata } from 'next';
import DashboardLayout from '../components/layout/DashboardLayout';
import QueryProvider from '../components/QueryProvider';

export const metadata: Metadata = {
  title: 'SGE Dashboard',
  description: 'Dashboard for SGE project management',
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
        <QueryProvider>
          <DashboardLayout>{children}</DashboardLayout>
        </QueryProvider>
      </body>
    </html>
  );
}
