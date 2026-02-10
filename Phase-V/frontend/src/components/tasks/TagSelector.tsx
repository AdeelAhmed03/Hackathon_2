'use client';

/**
 * TagSelector Component
 *
 * T092-T093: Multi-select tag component for TaskForm.
 */

import React, { useState, useEffect, useRef } from 'react';
import { Tag } from '../../types/task';

interface TagSelectorProps {
  availableTags: Tag[];
  selectedTagIds: number[];
  onChange: (tagIds: number[]) => void;
  onCreateTag?: (name: string) => Promise<Tag>;
  className?: string;
}

const TagSelector: React.FC<TagSelectorProps> = ({
  availableTags,
  selectedTagIds,
  onChange,
  onCreateTag,
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const selectedTags = availableTags.filter(tag => selectedTagIds.includes(tag.id));
  const filteredTags = availableTags.filter(tag =>
    tag.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleTagToggle = (tagId: number) => {
    if (selectedTagIds.includes(tagId)) {
      onChange(selectedTagIds.filter(id => id !== tagId));
    } else {
      onChange([...selectedTagIds, tagId]);
    }
  };

  const handleRemoveTag = (tagId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    onChange(selectedTagIds.filter(id => id !== tagId));
  };

  const handleCreateTag = async () => {
    if (!onCreateTag || !searchTerm.trim()) return;

    setIsCreating(true);
    try {
      const newTag = await onCreateTag(searchTerm.trim());
      onChange([...selectedTagIds, newTag.id]);
      setSearchTerm('');
    } catch (error) {
      console.error('Failed to create tag:', error);
    } finally {
      setIsCreating(false);
    }
  };

  const showCreateOption = onCreateTag &&
    searchTerm.trim() &&
    !availableTags.some(tag => tag.name.toLowerCase() === searchTerm.toLowerCase());

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Selected Tags Display */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="min-h-[42px] px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                 bg-white dark:bg-gray-700 cursor-pointer
                 focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-transparent"
      >
        <div className="flex flex-wrap gap-1">
          {selectedTags.map((tag) => (
            <span
              key={tag.id}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-sm
                       bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200"
            >
              {tag.name}
              <button
                onClick={(e) => handleRemoveTag(tag.id, e)}
                className="hover:text-blue-600 dark:hover:text-blue-100"
              >
                <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </span>
          ))}
          {selectedTags.length === 0 && (
            <span className="text-gray-400 dark:text-gray-500">Select tags...</span>
          )}
        </div>
      </div>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg">
          {/* Search Input */}
          <div className="p-2 border-b border-gray-200 dark:border-gray-700">
            <input
              type="text"
              placeholder="Search or create tag..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                       focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              autoFocus
            />
          </div>

          {/* Tag List */}
          <div className="max-h-48 overflow-y-auto p-2">
            {filteredTags.length > 0 ? (
              <div className="space-y-1">
                {filteredTags.map((tag) => {
                  const isSelected = selectedTagIds.includes(tag.id);
                  return (
                    <button
                      key={tag.id}
                      onClick={() => handleTagToggle(tag.id)}
                      className={`w-full flex items-center justify-between px-3 py-2 rounded
                        transition-colors text-left
                        ${isSelected
                          ? 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200'
                          : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                        }`}
                    >
                      <span>{tag.name}</span>
                      {isSelected && (
                        <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </button>
                  );
                })}
              </div>
            ) : !showCreateOption && (
              <p className="text-center text-gray-500 dark:text-gray-400 py-4">
                No tags found
              </p>
            )}

            {/* Create New Tag Option */}
            {showCreateOption && (
              <button
                onClick={handleCreateTag}
                disabled={isCreating}
                className="w-full flex items-center gap-2 px-3 py-2 rounded
                         text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20
                         disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                {isCreating ? 'Creating...' : `Create "${searchTerm}"`}
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default TagSelector;
