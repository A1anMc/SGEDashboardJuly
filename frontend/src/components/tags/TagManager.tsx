'use client';

import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Tag, TagCategory } from '@/types/models';

interface TagManagerProps {
  tags: Tag[];
  onDelete: (id: string) => void;
  onAdd: (name: string, category: TagCategory, description?: string, synonyms?: string[]) => void;
}

export default function TagManager({ tags, onDelete, onAdd }: TagManagerProps) {
  const [newTag, setNewTag] = useState({
    name: '',
    category: TagCategory.OTHER,
    description: '',
    synonyms: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTag.name || !newTag.category) return;

    onAdd(
      newTag.name,
      newTag.category,
      newTag.description || undefined,
      newTag.synonyms ? newTag.synonyms.split(',').map(s => s.trim()) : undefined
    );

    setNewTag({
      name: '',
      category: TagCategory.OTHER,
      description: '',
      synonyms: '',
    });
  };

  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="space-y-4 bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Input
            placeholder="Tag name"
            value={newTag.name}
            onChange={(e) => setNewTag({ ...newTag, name: e.target.value })}
            required
          />
          <Select
            value={newTag.category}
            onValueChange={(value: TagCategory) => setNewTag({ ...newTag, category: value })}
          >
            {Object.values(TagCategory).map((category) => (
              <option key={category} value={category}>
                {category.replace(/_/g, ' ').toUpperCase()}
              </option>
            ))}
          </Select>
          <Input
            placeholder="Description (optional)"
            value={newTag.description}
            onChange={(e) => setNewTag({ ...newTag, description: e.target.value })}
          />
          <Input
            placeholder="Synonyms (comma-separated)"
            value={newTag.synonyms}
            onChange={(e) => setNewTag({ ...newTag, synonyms: e.target.value })}
          />
        </div>
        <Button type="submit">Add Tag</Button>
      </form>

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
          {tags.map((tag) => (
            <TableRow key={tag.id}>
              <TableCell>{tag.name}</TableCell>
              <TableCell>
                <Badge variant="secondary">
                  {tag.category.replace(/_/g, ' ').toUpperCase()}
                </Badge>
              </TableCell>
              <TableCell>{tag.description || '-'}</TableCell>
              <TableCell>
                {tag.synonyms?.map((synonym) => (
                  <Badge key={synonym} variant="outline" className="mr-1">
                    {synonym}
                  </Badge>
                ))}
              </TableCell>
              <TableCell>
                <div className="flex gap-2">
                  <Badge variant="default">{tag.grant_count || 0} Grants</Badge>
                  <Badge variant="default">{tag.project_count || 0} Projects</Badge>
                </div>
              </TableCell>
              <TableCell>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => onDelete(tag.id)}
                >
                  Delete
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
} 