import React from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { grantsApi } from '../../services/grants';
import { CreateGrantInput, Grant } from '../../types/models';
import { toast } from 'react-hot-toast';
import { format } from 'date-fns';

interface GrantFormProps {
  grant?: Grant;
  onClose: () => void;
}

export function GrantForm({ grant, onClose }: GrantFormProps) {
  const queryClient = useQueryClient();
  const defaultValues = {
    title: grant?.title || '',
    description: grant?.description || '',
    amount: grant?.amount || 0,
    deadline: grant?.deadline ? format(new Date(grant.deadline), 'yyyy-MM-dd') : '',
    status: grant?.status || 'draft',
    tags: grant?.tags || [],
    source_url: grant?.source_url || '',
    eligibility_criteria: grant?.eligibility_criteria || [],
  };

  const mutation = useMutation({
    mutationFn: (data: CreateGrantInput) => {
      return grant
        ? grantsApi.updateGrant(grant.id, data)
        : grantsApi.createGrant(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grants'] });
      toast.success(grant ? 'Grant updated successfully' : 'Grant created successfully');
      onClose();
    },
    onError: (error) => {
      toast.error('Failed to save grant');
      console.error('Error saving grant:', error);
    },
  });

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const data: CreateGrantInput = {
      title: formData.get('title') as string,
      description: formData.get('description') as string,
      amount: parseFloat(formData.get('amount') as string) || 0,
      due_date: formData.get('deadline') as string,
      status: formData.get('status') as 'open' | 'closed' | 'draft',
      source_url: formData.get('source_url') as string,
      eligibility_criteria: (formData.get('eligibility_criteria') as string)
        .split('\n')
        .filter(Boolean),
      tags: (formData.get('tags') as string).split(',').map(tag => tag.trim()).filter(Boolean),
    };
    mutation.mutate(data);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">Title</label>
        <input
          type="text"
          name="title"
          defaultValue={defaultValues.title}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Description</label>
        <textarea
          name="description"
          defaultValue={defaultValues.description}
          rows={4}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Amount</label>
        <input
          type="number"
          name="amount"
          defaultValue={defaultValues.amount}
          required
          min="0"
          step="0.01"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Deadline</label>
        <input
          type="date"
          name="deadline"
          defaultValue={defaultValues.deadline}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Status</label>
        <select
          name="status"
          defaultValue={defaultValues.status}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        >
          <option value="draft">Draft</option>
          <option value="open">Open</option>
          <option value="closed">Closed</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Source URL</label>
        <input
          type="url"
          name="source_url"
          defaultValue={defaultValues.source_url}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Eligibility Criteria (one per line)
        </label>
        <textarea
          name="eligibility_criteria"
          defaultValue={defaultValues.eligibility_criteria.join('\n')}
          rows={4}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Tags (comma separated)
        </label>
        <input
          type="text"
          name="tags"
          defaultValue={defaultValues.tags.join(', ')}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
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
          disabled={mutation.isPending}
          className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:opacity-50"
        >
          {mutation.isPending ? 'Saving...' : grant ? 'Update Grant' : 'Create Grant'}
        </button>
      </div>
    </form>
  );
} 