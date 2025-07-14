import dynamic from 'next/dynamic';
import { LoadingState } from '../ui/loading-state';

// Dynamic import for the heavy TagManager component
const TagManagerComponent = dynamic(
  () => import('./TagManagerComponent'),
  {
    loading: () => <LoadingState message="Loading tag manager..." />,
    ssr: true, // Enable SSR for table data
  }
);

export const TagManager = TagManagerComponent; 