import { Metadata } from 'next';
import { TagManager } from '../../../../components/tags/TagManager';

export const metadata: Metadata = {
  title: 'Tag Management - SGE Dashboard',
  description: 'Manage tags and controlled vocabularies for the SGE Dashboard',
};

export default function TagManagementPage() {
  return (
    <div className="container mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Tag Management</h1>
        <p className="text-gray-600 mt-2">
          Manage controlled vocabularies for grants, projects, and tasks.
        </p>
      </div>
      
      <TagManager />
    </div>
  );
} 