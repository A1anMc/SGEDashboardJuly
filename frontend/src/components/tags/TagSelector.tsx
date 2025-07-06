'use client';

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../services/api';
import { Tag } from '../../types/models';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from '../ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '../ui/popover';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { X } from 'lucide-react';

interface TagSelectorProps {
  selectedTags: string[];
  onTagsChange: (tags: string[]) => void;
}

export function TagSelector({ selectedTags, onTagsChange }: TagSelectorProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');

  const { data: tags } = useQuery({
    queryKey: ['tags'],
    queryFn: async () => {
      const response = await api.get<Tag[]>('/tags');
      return response.data;
    },
  });

  const filteredTags = tags?.filter((tag) =>
    tag.name.toLowerCase().includes(search.toLowerCase())
  );

  const handleSelect = (tagId: string) => {
    if (selectedTags.includes(tagId)) {
      onTagsChange(selectedTags.filter((id) => id !== tagId));
    } else {
      onTagsChange([...selectedTags, tagId]);
    }
  };

  const handleRemove = (tagId: string) => {
    onTagsChange(selectedTags.filter((id) => id !== tagId));
  };

  return (
    <div className="space-y-2">
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className="w-full justify-between"
          >
            Select tags...
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[400px] p-0">
          <Command>
            <CommandInput
              placeholder="Search tags..."
              value={search}
              onValueChange={setSearch}
            />
            <CommandEmpty>No tags found.</CommandEmpty>
            <CommandGroup>
              {filteredTags?.map((tag) => (
                <CommandItem
                  key={tag.id}
                  value={tag.name}
                  onSelect={() => handleSelect(tag.id)}
                >
                  <div
                    className="w-3 h-3 rounded-full mr-2"
                    style={{ backgroundColor: tag.color || '#000000' }}
                  />
                  {tag.name}
                  {selectedTags.includes(tag.id) && (
                    <span className="ml-auto text-green-600">✓</span>
                  )}
                </CommandItem>
              ))}
            </CommandGroup>
          </Command>
        </PopoverContent>
      </Popover>

      <div className="flex flex-wrap gap-2">
        {selectedTags.map((tagId) => {
          const tag = tags?.find((t) => t.id === tagId);
          if (!tag) return null;
          return (
            <Badge
              key={tag.id}
              variant="secondary"
              className="flex items-center gap-1"
            >
              <div
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: tag.color || '#000000' }}
              />
              {tag.name}
              <button
                className="ml-1 hover:text-destructive"
                onClick={() => handleRemove(tag.id)}
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          );
        })}
      </div>
    </div>
  );
} 