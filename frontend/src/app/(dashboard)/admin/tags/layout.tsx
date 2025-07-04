import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Tag Management - SGE Dashboard',
  description: 'Manage tags and controlled vocabularies for the SGE Dashboard',
};

export default function TagsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
} 