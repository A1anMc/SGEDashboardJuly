import dynamic from 'next/dynamic';
import { LoadingState } from '../ui/loading-state';

// Dynamic import for the heavy GrantDashboard component
const GrantDashboardComponent = dynamic(
  () => import('./GrantDashboardComponent'),
  {
    loading: () => <LoadingState message="Loading dashboard..." />,
    ssr: false, // Disable SSR for charts
  }
);

export default GrantDashboardComponent; 