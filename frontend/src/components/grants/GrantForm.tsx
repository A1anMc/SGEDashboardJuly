import React from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { Grant } from '@/types/models';
import { useCreateGrant, useUpdateGrant } from '@/hooks/useGrants';

interface GrantFormProps {
  grant?: Grant;
  onClose: () => void;
}

export function GrantForm({ grant, onClose }: GrantFormProps) {
  const queryClient = useQueryClient();
  const createGrantMutation = useCreateGrant();
  const updateGrantMutation = useUpdateGrant();

  const defaultValues = {
    title: grant?.title || '',
    description: grant?.description || '',
    source: grant?.source || '',
    source_url: grant?.source_url || '',
    application_url: grant?.application_url || '',
    contact_email: grant?.contact_email || '',
    min_amount: grant?.min_amount || '',
    max_amount: grant?.max_amount || '',
    open_date: grant?.open_date ? new Date(grant.open_date).toISOString().split('T')[0] : '',
    deadline: grant?.deadline ? new Date(grant.deadline).toISOString().split('T')[0] : '',
    industry_focus: grant?.industry_focus || '',
    location_eligibility: grant?.location_eligibility || '',
    org_type_eligible: grant?.org_type_eligible?.join(', ') || '',
    funding_purpose: grant?.funding_purpose?.join(', ') || '',
    audience_tags: grant?.audience_tags?.join(', ') || '',
    status: grant?.status || 'draft',
    notes: grant?.notes || '',
    tags: grant?.tags?.map(tag => tag.name).join(', ') || '',
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const data = {
      title: formData.get('title') as string,
      description: formData.get('description') as string,
      source: formData.get('source') as string,
      source_url: formData.get('source_url') as string,
      application_url: formData.get('application_url') as string,
      contact_email: formData.get('contact_email') as string,
      min_amount: parseFloat(formData.get('min_amount') as string) || undefined,
      max_amount: parseFloat(formData.get('max_amount') as string) || undefined,
      open_date: formData.get('open_date') as string,
      deadline: formData.get('deadline') as string,
      industry_focus: formData.get('industry_focus') as string,
      location_eligibility: formData.get('location_eligibility') as string,
      org_type_eligible: (formData.get('org_type_eligible') as string)
        .split(',')
        .map(type => type.trim())
        .filter(Boolean),
      funding_purpose: (formData.get('funding_purpose') as string)
        .split(',')
        .map(purpose => purpose.trim())
        .filter(Boolean),
      audience_tags: (formData.get('audience_tags') as string)
        .split(',')
        .map(tag => tag.trim())
        .filter(Boolean),
      status: formData.get('status') as 'draft' | 'open' | 'closed' | 'archived',
      notes: formData.get('notes') as string,
      tags: (formData.get('tags') as string)
        .split(',')
        .map(tag => tag.trim())
        .filter(Boolean),
    };

    if (grant) {
      updateGrantMutation.mutate({ id: grant.id.toString(), grantInput: data });
    } else {
      createGrantMutation.mutate(data);
    }
  };

  // Handle success/error for both mutations
  React.useEffect(() => {
    if (createGrantMutation.isSuccess) {
      toast.success('Grant created successfully');
      onClose();
    }
    if (updateGrantMutation.isSuccess) {
      toast.success('Grant updated successfully');
      onClose();
    }
    if (createGrantMutation.isError) {
      toast.error('Failed to create grant');
    }
    if (updateGrantMutation.isError) {
      toast.error('Failed to update grant');
    }
  }, [createGrantMutation.isSuccess, updateGrantMutation.isSuccess, createGrantMutation.isError, updateGrantMutation.isError, onClose]);

  const isLoading = createGrantMutation.isPending || updateGrantMutation.isPending;

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
        <label className="block text-sm font-medium text-gray-700">Source</label>
        <input
          type="text"
          name="source"
          defaultValue={defaultValues.source}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
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
        <label className="block text-sm font-medium text-gray-700">Application URL</label>
        <input
          type="url"
          name="application_url"
          defaultValue={defaultValues.application_url}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Contact Email</label>
        <input
          type="email"
          name="contact_email"
          defaultValue={defaultValues.contact_email}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Minimum Amount</label>
          <input
            type="number"
            name="min_amount"
            defaultValue={defaultValues.min_amount}
            min="0"
            step="0.01"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Maximum Amount</label>
          <input
            type="number"
            name="max_amount"
            defaultValue={defaultValues.max_amount}
            min="0"
            step="0.01"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Open Date</label>
          <input
            type="date"
            name="open_date"
            defaultValue={defaultValues.open_date}
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
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Industry Focus</label>
        <select
          name="industry_focus"
          defaultValue={defaultValues.industry_focus}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        >
          <option value="">Select Industry Focus</option>
          <option value="technology">Technology</option>
          <option value="healthcare">Healthcare</option>
          <option value="education">Education</option>
          <option value="environment">Environment</option>
          <option value="agriculture">Agriculture</option>
          <option value="manufacturing">Manufacturing</option>
          <option value="services">Services</option>
          <option value="research">Research</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Location Eligibility</label>
        <select
          name="location_eligibility"
          defaultValue={defaultValues.location_eligibility}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        >
          <option value="">Select Location Eligibility</option>
          <option value="national">National</option>
          <option value="state">State</option>
          <option value="regional">Regional</option>
          <option value="local">Local</option>
          <option value="international">International</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Organization Types (comma separated)
        </label>
        <input
          type="text"
          name="org_type_eligible"
          defaultValue={defaultValues.org_type_eligible}
          placeholder="startup, sme, enterprise, nonprofit, government, academic, any"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Funding Purpose (comma separated)
        </label>
        <input
          type="text"
          name="funding_purpose"
          defaultValue={defaultValues.funding_purpose}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Audience Tags (comma separated)
        </label>
        <input
          type="text"
          name="audience_tags"
          defaultValue={defaultValues.audience_tags}
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
          <option value="archived">Archived</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Notes</label>
        <textarea
          name="notes"
          defaultValue={defaultValues.notes}
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
          defaultValue={defaultValues.tags}
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
          disabled={isLoading}
          className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:opacity-50"
        >
          {isLoading ? 'Saving...' : grant ? 'Update Grant' : 'Create Grant'}
        </button>
      </div>
    </form>
  );
} 