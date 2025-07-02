import React, { useState, useEffect } from 'react';
import { Tag, TagCategory } from '@/types/models';
import { getTags } from '@/services/tags';

interface TagSelectorProps {
  selectedTags: Tag[];
  onTagsChange: (tags: Tag[]) => void;
  category?: TagCategory;
  multiple?: boolean;
  placeholder?: string;
}

export const TagSelector: React.FC<TagSelectorProps> = ({
  selectedTags,
  onTagsChange,
  category,
  multiple = true,
  placeholder = 'Select tags...',
}) => {
  const [tags, setTags] = useState<Tag[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    loadTags();
  }, [category]);

  const loadTags = async () => {
    try {
      const fetchedTags = await getTags(category);
      setTags(fetchedTags);
    } catch (error) {
      console.error('Error loading tags:', error);
    }
  };

  const filteredTags = tags.filter(
    (tag) =>
      tag.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
      !selectedTags.find((selected) => selected.id === tag.id)
  );

  const handleSelectTag = (tag: Tag) => {
    if (multiple) {
      onTagsChange([...selectedTags, tag]);
    } else {
      onTagsChange([tag]);
      setIsOpen(false);
    }
    setSearchTerm('');
  };

  const handleRemoveTag = (tagId: number) => {
    onTagsChange(selectedTags.filter((tag) => tag.id !== tagId));
  };

  return (
    <div className="relative">
      <div
        className="border rounded-md p-2 min-h-[40px] cursor-text"
        onClick={() => setIsOpen(true)}
      >
        <div className="flex flex-wrap gap-2">
          {selectedTags.map((tag) => (
            <div
              key={tag.id}
              className="bg-blue-100 text-blue-800 px-2 py-1 rounded-md flex items-center gap-1"
            >
              <span>{tag.name}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleRemoveTag(tag.id);
                }}
                className="text-blue-600 hover:text-blue-800"
              >
                ×
              </button>
            </div>
          ))}
          {isOpen && (
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="outline-none flex-1 min-w-[100px]"
              placeholder={selectedTags.length === 0 ? placeholder : ''}
              autoFocus
            />
          )}
        </div>
      </div>

      {isOpen && (
        <>
          <div
            className="fixed inset-0"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute z-10 w-full mt-1 bg-white border rounded-md shadow-lg max-h-60 overflow-auto">
            {filteredTags.length === 0 ? (
              <div className="p-2 text-gray-500">No tags found</div>
            ) : (
              filteredTags.map((tag) => (
                <div
                  key={tag.id}
                  className="p-2 hover:bg-gray-100 cursor-pointer"
                  onClick={() => handleSelectTag(tag)}
                >
                  <div className="font-medium">{tag.name}</div>
                  {tag.description && (
                    <div className="text-sm text-gray-500">{tag.description}</div>
                  )}
                </div>
              ))
            )}
          </div>
        </>
      )}
    </div>
  );
}; 