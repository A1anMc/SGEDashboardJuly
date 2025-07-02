import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Tag, TagCategory } from '@/types/models';
import { tagsApi } from '@/services/tags';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';

interface TagSelectorProps {
  selectedTags: number[];
  onTagsChange: (tagIds: number[]) => void;
  category?: TagCategory;
  placeholder?: string;
  maxTags?: number;
  disabled?: boolean;
}

export function TagSelector({
  selectedTags,
  onTagsChange,
  category,
  placeholder = "Select tags...",
  maxTags = Infinity,
  disabled = false
}: TagSelectorProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  
  // Fetch available tags
  const { data: tags, isLoading } = useQuery({
    queryKey: ['tags', category, searchTerm],
    queryFn: async () => {
      if (searchTerm) {
        return tagsApi.searchTags(searchTerm, category);
      } else if (category) {
        return tagsApi.getTagsByCategory(category);
      } else {
        const response = await tagsApi.getTags();
        return response.items;
      }
    },
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });
  
  // Fetch selected tags details
  const { data: selectedTagDetails } = useQuery({
    queryKey: ['tags', 'selected', selectedTags],
    queryFn: async () => {
      const details = await Promise.all(
        selectedTags.map(id => tagsApi.getTag(id))
      );
      return details;
    },
    enabled: selectedTags.length > 0,
  });
  
  const handleTagSelect = (tagId: number) => {
    if (selectedTags.includes(tagId)) {
      onTagsChange(selectedTags.filter(id => id !== tagId));
    } else if (selectedTags.length < maxTags) {
      onTagsChange([...selectedTags, tagId]);
    }
    setIsOpen(false);
  };
  
  const handleTagRemove = (tagId: number) => {
    onTagsChange(selectedTags.filter(id => id !== tagId));
  };
  
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };
  
  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2 min-h-[2.5rem] p-2 border rounded-md">
        {selectedTagDetails?.map((tag) => (
          <Badge
            key={tag.id}
            variant="secondary"
            className="flex items-center gap-1"
          >
            {tag.name}
            <Button
              variant="ghost"
              size="sm"
              className="h-4 w-4 p-0"
              onClick={() => handleTagRemove(tag.id)}
              disabled={disabled}
            >
              <X className="h-3 w-3" />
            </Button>
          </Badge>
        ))}
        {selectedTags.length < maxTags && (
          <div className="flex-1">
            <Select
              open={isOpen}
              onOpenChange={setIsOpen}
              disabled={disabled}
            >
              <SelectTrigger className="border-0 p-0 h-auto min-h-0">
                <SelectValue placeholder={placeholder} />
              </SelectTrigger>
              <SelectContent>
                <div className="p-2">
                  <Input
                    placeholder="Search tags..."
                    value={searchTerm}
                    onChange={handleSearchChange}
                    className="mb-2"
                  />
                </div>
                <div className="max-h-[200px] overflow-y-auto">
                  {isLoading ? (
                    <div className="p-2 text-center text-gray-500">
                      Loading...
                    </div>
                  ) : tags?.length === 0 ? (
                    <div className="p-2 text-center text-gray-500">
                      No tags found
                    </div>
                  ) : (
                    tags?.map((tag) => (
                      <SelectItem
                        key={tag.id}
                        value={tag.id.toString()}
                        onSelect={() => handleTagSelect(tag.id)}
                        disabled={
                          selectedTags.includes(tag.id) ||
                          (selectedTags.length >= maxTags)
                        }
                      >
                        <div className="flex items-center justify-between">
                          <span>{tag.name}</span>
                          {tag.description && (
                            <span className="text-sm text-gray-500">
                              {tag.description}
                            </span>
                          )}
                        </div>
                      </SelectItem>
                    ))
                  )}
                </div>
              </SelectContent>
            </Select>
          </div>
        )}
      </div>
      {maxTags < Infinity && (
        <p className="text-sm text-gray-500">
          {selectedTags.length} of {maxTags} tags selected
        </p>
      )}
    </div>
  );
} 