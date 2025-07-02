import { FC, useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { grantsApi } from '@/services/grants';
import { CreateGrantInput, Grant } from '@/types/models';
import { toast } from 'react-hot-toast';

interface GrantFormProps {
  grant?: Grant;
  onClose: () => void;
}

export const GrantForm: FC<GrantFormProps> = ({ grant, onClose }) => {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState<CreateGrantInput>({
    title: grant?.title || '',
    description: grant?.description || '',
    amount: grant?.amount || undefined,
    deadline: grant?.deadline?.split('T')[0] || '',
    status: grant?.status || 'draft',
    tags: grant?.tags || [],
    source_url: grant?.source_url || '',
    source: grant?.source || '',
    notes: grant?.notes || '',
  });

  const createMutation = useMutation({
    mutationFn: grantsApi.createGrant,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grants'] });
      toast.success('Grant created successfully');
      onClose();
    },
    onError: (error: Error) => {
      toast.error(`Error creating grant: ${error.message}`);
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: CreateGrantInput) =>
      grantsApi.updateGrant(grant!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grants'] });
      toast.success('Grant updated successfully');
      onClose();
    },
    onError: (error: Error) => {
      toast.error(`Error updating grant: ${error.message}`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (grant) {
      updateMutation.mutate(formData);
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleTagsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const tags = e.target.value.split(',').map((tag) => tag.trim());
    setFormData({ ...formData, tags });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">Title</label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Description
        </label>
        <textarea
          value={formData.description}
          onChange={(e) =>
            setFormData({ ...formData, description: e.target.value })
          }
          rows={4}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          required
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Amount
          </label>
          <input
            type="number"
            value={formData.amount || ''}
            onChange={(e) =>
              setFormData({
                ...formData,
                amount: e.target.value ? Number(e.target.value) : undefined,
              })
            }
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Deadline
          </label>
          <input
            type="date"
            value={formData.deadline}
            onChange={(e) =>
              setFormData({ ...formData, deadline: e.target.value })
            }
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Status</label>
        <select
          value={formData.status}
          onChange={(e) =>
            setFormData({
              ...formData,
              status: e.target.value as 'open' | 'closed' | 'draft',
            })
          }
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="draft">Draft</option>
          <option value="open">Open</option>
          <option value="closed">Closed</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Tags (comma-separated)
        </label>
        <input
          type="text"
          value={formData.tags.join(', ')}
          onChange={handleTagsChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Source</label>
        <input
          type="text"
          value={formData.source}
          onChange={(e) => setFormData({ ...formData, source: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Source URL
        </label>
        <input
          type="url"
          value={formData.source_url || ''}
          onChange={(e) =>
            setFormData({ ...formData, source_url: e.target.value })
          }
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Notes</label>
        <textarea
          value={formData.notes || ''}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          rows={3}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <div className="flex justify-end space-x-3">
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={createMutation.isPending || updateMutation.isPending}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {createMutation.isPending || updateMutation.isPending
            ? 'Saving...'
            : grant
            ? 'Update Grant'
            : 'Create Grant'}
        </button>
      </div>
    </form>
  );
}; 