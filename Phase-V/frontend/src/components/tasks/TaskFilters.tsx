'use client';

/**
 * TaskFilters Component
 *
 * T102-T106: Filter, search, and sort controls for task list.
 * T111-T112: Multi-field sort selector and direction toggle.
 */

import React, { useState, useEffect } from 'react';
import { TaskStatus, TaskPriority, TaskFilters as TaskFiltersType, Tag } from '../../types/task';

interface TaskFiltersProps {
  filters: TaskFiltersType;
  onFiltersChange: (filters: TaskFiltersType) => void;
  availableTags: Tag[];
  className?: string;
}

const TaskFilters: React.FC<TaskFiltersProps> = ({
  filters,
  onFiltersChange,
  availableTags,
  className = ''
}) => {
  const [searchValue, setSearchValue] = useState(filters.q || '');
  const [isExpanded, setIsExpanded] = useState(false);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchValue !== filters.q) {
        onFiltersChange({ ...filters, q: searchValue || undefined });
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchValue]);

  const handleStatusChange = (status: TaskStatus | '') => {
    onFiltersChange({
      ...filters,
      status: status || undefined
    });
  };

  const handlePriorityChange = (priority: TaskPriority | '') => {
    onFiltersChange({
      ...filters,
      priority: priority || undefined
    });
  };

  const handleTagToggle = (tagId: number) => {
    const currentTags = filters.tags || [];
    const newTags = currentTags.includes(tagId)
      ? currentTags.filter(id => id !== tagId)
      : [...currentTags, tagId];
    onFiltersChange({
      ...filters,
      tags: newTags.length > 0 ? newTags : undefined
    });
  };

  const handleSortChange = (sortBy: string) => {
    onFiltersChange({
      ...filters,
      sort_by: sortBy
    });
  };

  const handleSortOrderToggle = () => {
    onFiltersChange({
      ...filters,
      sort_order: filters.sort_order === 'asc' ? 'desc' : 'asc'
    });
  };

  const handleDueDateChange = (field: 'due_before' | 'due_after', value: string) => {
    onFiltersChange({
      ...filters,
      [field]: value || undefined
    });
  };

  const clearFilters = () => {
    setSearchValue('');
    onFiltersChange({
      page: 1,
      page_size: filters.page_size
    });
  };

  const hasActiveFilters = !!(
    filters.q ||
    filters.status ||
    filters.priority ||
    (filters.tags && filters.tags.length > 0) ||
    filters.due_before ||
    filters.due_after
  );

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow p-4 ${className}`}>
      {/* Search Input - T103 */}
      <div className="flex gap-2 items-center mb-4">
        <div className="relative flex-1">
          <input
            type="text"
            placeholder="Search tasks..."
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                     focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <svg
            className="absolute left-3 top-2.5 h-5 w-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300
                   bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600
                   transition-colors flex items-center gap-2"
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          Filters
          {hasActiveFilters && (
            <span className="bg-blue-500 text-white text-xs px-1.5 py-0.5 rounded-full">!</span>
          )}
        </button>

        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="px-3 py-2 text-sm text-red-600 hover:text-red-700 dark:text-red-400"
          >
            Clear
          </button>
        )}
      </div>

      {/* Expanded Filters */}
      {isExpanded && (
        <div className="border-t border-gray-200 dark:border-gray-700 pt-4 space-y-4">
          {/* Status and Priority Row */}
          <div className="flex flex-wrap gap-4">
            {/* Status Filter */}
            <div className="flex-1 min-w-[150px]">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Status
              </label>
              <select
                value={filters.status || ''}
                onChange={(e) => handleStatusChange(e.target.value as TaskStatus | '')}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                         bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              >
                <option value="">All</option>
                <option value={TaskStatus.PENDING}>Pending</option>
                <option value={TaskStatus.IN_PROGRESS}>In Progress</option>
                <option value={TaskStatus.COMPLETED}>Completed</option>
              </select>
            </div>

            {/* Priority Filter - T082 */}
            <div className="flex-1 min-w-[150px]">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Priority
              </label>
              <select
                value={filters.priority || ''}
                onChange={(e) => handlePriorityChange(e.target.value as TaskPriority | '')}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                         bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              >
                <option value="">All</option>
                <option value={TaskPriority.HIGH}>High</option>
                <option value={TaskPriority.MEDIUM}>Medium</option>
                <option value={TaskPriority.LOW}>Low</option>
              </select>
            </div>

            {/* Sort By - T111 */}
            <div className="flex-1 min-w-[150px]">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Sort By
              </label>
              <div className="flex gap-2">
                <select
                  value={filters.sort_by || 'created_at'}
                  onChange={(e) => handleSortChange(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                >
                  <option value="created_at">Created Date</option>
                  <option value="due_datetime">Due Date</option>
                  <option value="priority">Priority</option>
                  <option value="title">Title</option>
                  <option value="updated_at">Last Updated</option>
                </select>
                {/* Sort Order Toggle - T112 */}
                <button
                  onClick={handleSortOrderToggle}
                  className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
                  title={filters.sort_order === 'asc' ? 'Ascending' : 'Descending'}
                >
                  {filters.sort_order === 'asc' ? (
                    <svg className="h-5 w-5 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
                    </svg>
                  ) : (
                    <svg className="h-5 w-5 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4" />
                    </svg>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Date Range Filters - T104 */}
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Due After
              </label>
              <input
                type="datetime-local"
                value={filters.due_after || ''}
                onChange={(e) => handleDueDateChange('due_after', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                         bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              />
            </div>
            <div className="flex-1 min-w-[200px]">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Due Before
              </label>
              <input
                type="datetime-local"
                value={filters.due_before || ''}
                onChange={(e) => handleDueDateChange('due_before', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                         bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              />
            </div>
          </div>

          {/* Tag Filter - T094 */}
          {availableTags.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Tags (AND filter - tasks must have all selected tags)
              </label>
              <div className="flex flex-wrap gap-2">
                {availableTags.map((tag) => {
                  const isSelected = filters.tags?.includes(tag.id);
                  return (
                    <button
                      key={tag.id}
                      onClick={() => handleTagToggle(tag.id)}
                      className={`px-3 py-1 rounded-full text-sm font-medium transition-colors
                        ${isSelected
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                        }`}
                    >
                      {tag.name}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TaskFilters;
