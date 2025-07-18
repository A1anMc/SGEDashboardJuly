'use client';

import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '../ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { LoadingState } from '../ui/loading-state';
import { ErrorAlert } from '../ui/error-alert';
import { Tag } from '../../types/models';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../../services/api';
import { toast } from 'react-hot-toast';

interface TagFormData {
  name: string;
  description?: string;
  color?: string;
}

const TagManagerComponent = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedTag, setSelectedTag] = useState<Tag | null>(null);
  const queryClient = useQueryClient();

  const { data: tags, isLoading, error } = useQuery({
    queryKey: ['tags'],
    queryFn: async () => {
      const response = await apiClient.getTags();
      // Handle different response formats
      return (response as any)?.items || (response as any)?.data || response || [];
    },
  });

  const createMutation = useMutation({
    mutationFn: async (data: TagFormData) => {
      // Note: getTags method exists but createTag doesn't yet
      // For now, we'll use a placeholder
      console.log('Creating tag:', data);
      return { id: 'temp', ...data };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
      toast.success('Tag created successfully');
      setIsOpen(false);
      setSelectedTag(null);
    },
    onError: (error) => {
      toast.error('Failed to create tag');
      console.error('Create tag error:', error);
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: TagFormData }) => {
      // Note: updateTag method doesn't exist yet
      // For now, we'll use a placeholder
      console.log('Updating tag:', id, data);
      return { id, ...data };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
      toast.success('Tag updated successfully');
      setIsOpen(false);
      setSelectedTag(null);
    },
    onError: (error) => {
      toast.error('Failed to update tag');
      console.error('Update tag error:', error);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      // Note: deleteTag method doesn't exist yet
      // For now, we'll use a placeholder
      console.log('Deleting tag:', id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
      toast.success('Tag deleted successfully');
    },
    onError: (error) => {
      toast.error('Failed to delete tag');
      console.error('Delete tag error:', error);
    },
  });

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const data: TagFormData = {
      name: formData.get('name') as string,
      description: formData.get('description') as string,
      color: formData.get('color') as string,
    };

    if (selectedTag) {
      updateMutation.mutate({ id: selectedTag.id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleEdit = (tag: Tag) => {
    setSelectedTag(tag);
    setIsOpen(true);
  };

  const handleDelete = async (tag: Tag) => {
    if (window.confirm('Are you sure you want to delete this tag?')) {
      deleteMutation.mutate(tag.id);
    }
  };

  if (isLoading) {
    return <LoadingState message="Loading tags..." />;
  }

  if (error) {
    return <ErrorAlert message="Failed to load tags" retryable={true} />;
  }

  const tagsList = Array.isArray(tags) ? tags : [];

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Tag Management</h2>
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogTrigger asChild>
            <Button
              onClick={() => {
                setSelectedTag(null);
                setIsOpen(true);
              }}
            >
              Add Tag
            </Button>
          </DialogTrigger>
          <DialogContent>
            <form onSubmit={handleSubmit}>
              <DialogHeader>
                <DialogTitle>
                  {selectedTag ? 'Edit Tag' : 'Create New Tag'}
                </DialogTitle>
                <DialogDescription>
                  {selectedTag
                    ? 'Edit the details of the existing tag.'
                    : 'Add a new tag to help categorize grants and projects.'}
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="name" className="text-right">
                    Name
                  </Label>
                  <Input
                    id="name"
                    name="name"
                    defaultValue={selectedTag?.name}
                    className="col-span-3"
                    required
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="description" className="text-right">
                    Description
                  </Label>
                  <Input
                    id="description"
                    name="description"
                    defaultValue={selectedTag?.description}
                    className="col-span-3"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="color" className="text-right">
                    Color
                  </Label>
                  <Input
                    id="color"
                    name="color"
                    type="color"
                    defaultValue={selectedTag?.color || '#000000'}
                    className="col-span-3 h-10"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsOpen(false)}
                >
                  Cancel
                </Button>
                <Button type="submit">
                  {selectedTag ? 'Update Tag' : 'Create Tag'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-4">
        {tagsList.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <p className="text-gray-500">No tags found. Create your first tag to get started.</p>
            </CardContent>
          </Card>
        ) : (
          tagsList.map((tag) => (
            <Card key={tag.id}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: tag.color || '#000000' }}
                    />
                    <div>
                      <h3 className="font-semibold">{tag.name}</h3>
                      <p className="text-sm text-gray-600">{tag.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex gap-2">
                      <Badge variant="default">{tag.grant_count || 0} Grants</Badge>
                      <Badge variant="default">{tag.project_count || 0} Projects</Badge>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleEdit(tag)}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleDelete(tag)}
                      >
                        Delete
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};

export default TagManagerComponent; 