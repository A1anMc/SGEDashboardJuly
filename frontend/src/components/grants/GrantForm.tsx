import { FC, useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { grantsApi } from '@/services/grants';
import { CreateGrantRequest, Grant } from '@/types/models';
import { toast } from 'react-hot-toast';

interface GrantFormProps {
  grant?: Grant;
  onClose: () => void;
}

export const GrantForm: FC<GrantFormProps> = ({ grant, onClose }) => {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState<CreateGrantRequest>({
    title: grant?.title || '',
    description: grant?.description || '',
    source: grant?.source || '',
    industry_focus: grant?.industry_focus || 'general',
    location_eligibility: grant?.location_eligibility || 'Australia',
    org_type_eligible: grant?.org_type_eligible || [],
    funding_purpose: grant?.funding_purpose || [],
    audience_tags: grant?.audience_tags || [],
    open_date: grant?.open_date ? new Date(grant.open_date) : new Date(),
    deadline: grant?.deadline ? new Date(grant.deadline) : new Date(),
    min_amount: grant?.min_amount,
    max_amount: grant?.max_amount,
    application_url: grant?.application_url || '',
    contact_email: grant?.contact_email || '',
    notes: grant?.notes || '',
  });

  const createMutation = useMutation({
    mutationFn: grantsApi.createGrant,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grants'] });
      queryClient.invalidateQueries({ queryKey: ['grants', 'dashboard'] });
      toast.success('Grant created successfully');
      onClose();
    },
    onError: (error: Error) => {
      toast.error(`Error creating grant: ${error.message}`);
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: CreateGrantRequest) =>
      grantsApi.updateGrant(grant!.id, { ...data, id: grant!.id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grants'] });
      queryClient.invalidateQueries({ queryKey: ['grants', 'dashboard'] });
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

  const handleArrayFieldChange = (field: keyof CreateGrantRequest, value: string) => {
    const arrayValue = value.split(',').map((item) => item.trim()).filter(Boolean);
    setFormData({ ...formData, [field]: arrayValue });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-4xl mx-auto">
      {/* Basic Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Title *</label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Source *</label>
          <input
            type="text"
            value={formData.source}
            onChange={(e) => setFormData({ ...formData, source: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            required
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Description *</label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          rows={4}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          required
        />
      </div>

      {/* Matching Criteria */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Industry Focus</label>
          <select
            value={formData.industry_focus}
            onChange={(e) => setFormData({ ...formData, industry_focus: e.target.value as any })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="media">Media</option>
            <option value="creative_arts">Creative Arts</option>
            <option value="technology">Technology</option>
            <option value="general">General</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Location Eligibility</label>
          <select
            value={formData.location_eligibility}
            onChange={(e) => setFormData({ ...formData, location_eligibility: e.target.value as any })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="Australia">Australia (National)</option>
            <option value="VIC">Victoria</option>
            <option value="NSW">New South Wales</option>
            <option value="QLD">Queensland</option>
            <option value="SA">South Australia</option>
            <option value="WA">Western Australia</option>
            <option value="TAS">Tasmania</option>
            <option value="NT">Northern Territory</option>
            <option value="ACT">Australian Capital Territory</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Eligible Organization Types (comma-separated)
        </label>
        <input
          type="text"
          value={formData.org_type_eligible.join(', ')}
          onChange={(e) => handleArrayFieldChange('org_type_eligible', e.target.value)}
          placeholder="e.g., social_enterprise, not_for_profit, small_medium_enterprise"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Funding Purposes (comma-separated)
        </label>
        <input
          type="text"
          value={formData.funding_purpose.join(', ')}
          onChange={(e) => handleArrayFieldChange('funding_purpose', e.target.value)}
          placeholder="e.g., equipment, capacity building, research"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Audience Tags (comma-separated)
        </label>
        <input
          type="text"
          value={formData.audience_tags.join(', ')}
          onChange={(e) => handleArrayFieldChange('audience_tags', e.target.value)}
          placeholder="e.g., youth, community, artists"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      {/* Timing and Amount */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Open Date *</label>
          <input
            type="date"
            value={formData.open_date.toISOString().split('T')[0]}
            onChange={(e) => setFormData({ ...formData, open_date: new Date(e.target.value) })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Deadline *</label>
          <input
            type="date"
            value={formData.deadline.toISOString().split('T')[0]}
            onChange={(e) => setFormData({ ...formData, deadline: new Date(e.target.value) })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Minimum Amount ($)</label>
          <input
            type="number"
            value={formData.min_amount || ''}
            onChange={(e) => setFormData({ 
              ...formData, 
              min_amount: e.target.value ? Number(e.target.value) : undefined 
            })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Maximum Amount ($)</label>
          <input
            type="number"
            value={formData.max_amount || ''}
            onChange={(e) => setFormData({ 
              ...formData, 
              max_amount: e.target.value ? Number(e.target.value) : undefined 
            })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Additional Information */}
      <div>
        <label className="block text-sm font-medium text-gray-700">Application URL</label>
        <input
          type="url"
          value={formData.application_url}
          onChange={(e) => setFormData({ ...formData, application_url: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Contact Email</label>
        <input
          type="email"
          value={formData.contact_email}
          onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Notes</label>
        <textarea
          value={formData.notes}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          rows={3}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      {/* Form Actions */}
      <div className="flex justify-end space-x-4 pt-4">
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={createMutation.isPending || updateMutation.isPending}
          className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
        >
          {createMutation.isPending || updateMutation.isPending 
            ? 'Saving...' 
            : grant ? 'Update Grant' : 'Create Grant'
          }
        </button>
      </div>
    </form>
  );
}; 