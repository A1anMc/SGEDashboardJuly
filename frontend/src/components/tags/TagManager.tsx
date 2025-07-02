import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { toast } from 'react-hot-toast';
import { TagCategory, Tag } from '@/types/models';
import { api } from '@/services/api';

interface TagFormData {
  name: string;
  category: TagCategory;
  description?: string;
  parent_id?: number;
  synonyms?: string[];
}

export function TagManager() {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<TagCategory | 'all'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [formData, setFormData] = useState<TagFormData>({
    name: '',
    category: TagCategory.INDUSTRY,
  });
  
  const queryClient = useQueryClient();
  
  // Fetch tags
  const { data: tags, isLoading } = useQuery({
    queryKey: ['tags', selectedCategory, searchTerm],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (selectedCategory !== 'all') params.append('category', selectedCategory);
      if (searchTerm) params.append('search', searchTerm);
      const response = await api.get(`/tags?${params.toString()}`);
      return response.data;
    },
  });
  
  // Create tag mutation
  const createTag = useMutation({
    mutationFn: async (data: TagFormData) => {
      const response = await api.post('/tags', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
      setIsOpen(false);
      setFormData({ name: '', category: TagCategory.INDUSTRY });
      toast.success('Tag created successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create tag');
    },
  });
  
  // Delete tag mutation
  const deleteTag = useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/tags/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
      toast.success('Tag deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete tag');
    },
  });
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createTag.mutate(formData);
  };
  
  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this tag?')) {
      deleteTag.mutate(id);
    }
  };
  
  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Tag Management</h1>
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogTrigger asChild>
            <Button>Create New Tag</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Tag</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="category">Category</Label>
                <Select
                  value={formData.category}
                  onValueChange={(value: TagCategory) =>
                    setFormData({ ...formData, category: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.values(TagCategory).map((category) => (
                      <SelectItem key={category} value={category}>
                        {category.replace('_', ' ').toUpperCase()}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                />
              </div>
              <div>
                <Label htmlFor="synonyms">Synonyms (comma-separated)</Label>
                <Input
                  id="synonyms"
                  value={formData.synonyms?.join(', ') || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      synonyms: e.target.value.split(',').map((s) => s.trim()),
                    })
                  }
                />
              </div>
              <Button type="submit" disabled={createTag.isPending}>
                {createTag.isPending ? 'Creating...' : 'Create Tag'}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>
      
      <div className="flex gap-4 mb-6">
        <div className="w-64">
          <Select
            value={selectedCategory}
            onValueChange={(value: TagCategory | 'all') => setSelectedCategory(value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Filter by category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Categories</SelectItem>
              {Object.values(TagCategory).map((category) => (
                <SelectItem key={category} value={category}>
                  {category.replace('_', ' ').toUpperCase()}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="flex-1">
          <Input
            placeholder="Search tags..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>
      
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Category</TableHead>
            <TableHead>Description</TableHead>
            <TableHead>Synonyms</TableHead>
            <TableHead>Usage</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            <TableRow>
              <TableCell colSpan={6} className="text-center">
                Loading...
              </TableCell>
            </TableRow>
          ) : tags?.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="text-center">
                No tags found
              </TableCell>
            </TableRow>
          ) : (
            tags?.map((tag: Tag) => (
              <TableRow key={tag.id}>
                <TableCell>{tag.name}</TableCell>
                <TableCell>
                  <Badge variant="secondary">
                    {tag.category.replace('_', ' ').toUpperCase()}
                  </Badge>
                </TableCell>
                <TableCell>{tag.description}</TableCell>
                <TableCell>
                  {tag.synonyms?.map((synonym) => (
                    <Badge key={synonym} variant="outline" className="mr-1">
                      {synonym}
                    </Badge>
                  ))}
                </TableCell>
                <TableCell>
                  <div className="flex gap-2">
                    <Badge variant="default">{tag.grant_count} Grants</Badge>
                    <Badge variant="default">{tag.project_count} Projects</Badge>
                  </div>
                </TableCell>
                <TableCell>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => handleDelete(tag.id)}
                  >
                    Delete
                  </Button>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
} 