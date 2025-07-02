import React, { useState, useEffect } from 'react';
import { Tag, TagCategory } from '@/types/models';
import { createTag, updateTag, deleteTag, getTags } from '@/services/tags';

interface TagManagerProps {
  onTagsChange?: (tags: Tag[]) => void;
}

export const TagManager: React.FC<TagManagerProps> = ({ onTagsChange }) => {
  const [tags, setTags] = useState<Tag[]>([]);
  const [selectedTag, setSelectedTag] = useState<Tag | null>(null);
  const [newTag, setNewTag] = useState({
    name: '',
    category: TagCategory.INDUSTRY,
    description: '',
  });

  useEffect(() => {
    loadTags();
  }, []);

  const loadTags = async () => {
    try {
      const fetchedTags = await getTags();
      setTags(fetchedTags);
      if (onTagsChange) onTagsChange(fetchedTags);
    } catch (error) {
      console.error('Error loading tags:', error);
    }
  };

  const handleCreateTag = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createTag(newTag);
      setNewTag({ name: '', category: TagCategory.INDUSTRY, description: '' });
      await loadTags();
    } catch (error) {
      console.error('Error creating tag:', error);
    }
  };

  const handleUpdateTag = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTag) return;
    try {
      await updateTag(selectedTag.id, selectedTag);
      setSelectedTag(null);
      await loadTags();
    } catch (error) {
      console.error('Error updating tag:', error);
    }
  };

  const handleDeleteTag = async (tagId: number) => {
    try {
      await deleteTag(tagId);
      await loadTags();
    } catch (error) {
      console.error('Error deleting tag:', error);
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Tag Management</h2>
      
      {/* Create Tag Form */}
      <form onSubmit={handleCreateTag} className="mb-8">
        <h3 className="text-lg font-semibold mb-2">Create New Tag</h3>
        <div className="space-y-4">
          <input
            type="text"
            value={newTag.name}
            onChange={(e) => setNewTag({ ...newTag, name: e.target.value })}
            placeholder="Tag Name"
            className="w-full p-2 border rounded"
          />
          <select
            value={newTag.category}
            onChange={(e) => setNewTag({ ...newTag, category: e.target.value as TagCategory })}
            className="w-full p-2 border rounded"
          >
            {Object.values(TagCategory).map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
          <textarea
            value={newTag.description}
            onChange={(e) => setNewTag({ ...newTag, description: e.target.value })}
            placeholder="Description"
            className="w-full p-2 border rounded"
          />
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Create Tag
          </button>
        </div>
      </form>

      {/* Tag List */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Existing Tags</h3>
        {tags.map((tag) => (
          <div key={tag.id} className="border p-4 rounded">
            <h4 className="font-medium">{tag.name}</h4>
            <p className="text-sm text-gray-600">Category: {tag.category}</p>
            <p className="text-sm text-gray-600">{tag.description}</p>
            <div className="mt-2 space-x-2">
              <button
                onClick={() => setSelectedTag(tag)}
                className="text-blue-500 hover:text-blue-600"
              >
                Edit
              </button>
              <button
                onClick={() => handleDeleteTag(tag.id)}
                className="text-red-500 hover:text-red-600"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Edit Tag Modal */}
      {selectedTag && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-4 rounded max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">Edit Tag</h3>
            <form onSubmit={handleUpdateTag} className="space-y-4">
              <input
                type="text"
                value={selectedTag.name}
                onChange={(e) => setSelectedTag({ ...selectedTag, name: e.target.value })}
                className="w-full p-2 border rounded"
              />
              <select
                value={selectedTag.category}
                onChange={(e) => setSelectedTag({ ...selectedTag, category: e.target.value as TagCategory })}
                className="w-full p-2 border rounded"
              >
                {Object.values(TagCategory).map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>
              <textarea
                value={selectedTag.description}
                onChange={(e) => setSelectedTag({ ...selectedTag, description: e.target.value })}
                className="w-full p-2 border rounded"
              />
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setSelectedTag(null)}
                  className="px-4 py-2 border rounded"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}; 