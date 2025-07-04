'use client';

import React from 'react';
import { Tag, TagCategory } from '@/types/models';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';

interface TagSelectorProps {
  tags: Tag[];
  selectedTags: string[];
  onTagSelect: (tagId: string) => void;
  onTagRemove: (tagId: string) => void;
  category?: TagCategory;
}

export default function TagSelector({
  tags,
  selectedTags,
  onTagSelect,
  onTagRemove,
  category,
}: TagSelectorProps) {
  const [open, setOpen] = React.useState(false);

  const filteredTags = category
    ? tags.filter((tag) => tag.category === category)
    : tags;

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap gap-2">
        {selectedTags.map((tagId) => {
          const tag = tags.find((t) => t.id === tagId);
          if (!tag) return null;
          return (
            <Badge
              key={tag.id}
              variant="secondary"
              className="flex items-center gap-1"
            >
              {tag.name}
              <button
                className="ml-1 hover:text-destructive"
                onClick={() => onTagRemove(tag.id)}
              >
                ×
              </button>
            </Badge>
          );
        })}
      </div>

      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className="justify-between"
          >
            Select tags...
          </Button>
        </PopoverTrigger>
        <PopoverContent className="p-0" align="start">
          <Command>
            <CommandInput placeholder="Search tags..." />
            <CommandEmpty>No tags found.</CommandEmpty>
            <CommandGroup>
              {filteredTags.map((tag) => {
                const isSelected = selectedTags.includes(tag.id);
                return (
                  <CommandItem
                    key={tag.id}
                    value={tag.name}
                    onSelect={() => {
                      if (isSelected) {
                        onTagRemove(tag.id);
                      } else {
                        onTagSelect(tag.id);
                      }
                    }}
                  >
                    <div className="flex items-center justify-between w-full">
                      <span>{tag.name}</span>
                      <Badge variant="outline" className="ml-2">
                        {tag.category.replace(/_/g, ' ').toUpperCase()}
                      </Badge>
                    </div>
                  </CommandItem>
                );
              })}
            </CommandGroup>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
} 