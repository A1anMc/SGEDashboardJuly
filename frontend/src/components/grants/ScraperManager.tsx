import dynamic from 'next/dynamic';
import { LoadingState } from '../ui/loading-state';

// Dynamic import for the heavy ScraperManager component
const ScraperManagerComponent = dynamic(
  () => import('./ScraperManagerComponent'),
  {
    loading: () => <LoadingState message="Loading scraper manager..." />,
    ssr: false, // Disable SSR for real-time updates
  }
);

export const ScraperManager = ScraperManagerComponent;