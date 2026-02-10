'use client';

/**
 * useTasks Hook
 *
 * T105: Hook to pass filter/search params to backend.
 * Manages task CRUD operations with filtering and pagination.
 */

import { useState, useEffect, useCallback } from 'react';
import {
  Task,
  Tag,
  TaskFilters,
  TaskListResponse,
  TaskCreatePayload,
  TaskUpdatePayload
} from '../types/task';

const API_BASE = '/api/tasks';
const TAGS_API = '/api/tags';

interface UseTasksOptions {
  initialFilters?: TaskFilters;
  autoFetch?: boolean;
}

interface UseTasksReturn {
  tasks: Task[];
  totalCount: number;
  page: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  filters: TaskFilters;
  setFilters: (filters: TaskFilters) => void;
  fetchTasks: () => Promise<void>;
  createTask: (payload: TaskCreatePayload) => Promise<Task>;
  updateTask: (id: number, payload: TaskUpdatePayload) => Promise<Task>;
  deleteTask: (id: number) => Promise<void>;
  completeTask: (id: number) => Promise<Task>;
  toggleTaskStatus: (id: number) => Promise<Task>;
  // Tags
  tags: Tag[];
  fetchTags: () => Promise<void>;
  createTag: (name: string) => Promise<Tag>;
  deleteTag: (id: number) => Promise<void>;
}

export function useTasks(options: UseTasksOptions = {}): UseTasksReturn {
  const { initialFilters = {}, autoFetch = true } = options;

  const [tasks, setTasks] = useState<Task[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<TaskFilters>(initialFilters);

  // Build query string from filters
  const buildQueryString = useCallback((filters: TaskFilters): string => {
    const params = new URLSearchParams();

    if (filters.q) params.append('q', filters.q);
    if (filters.status) params.append('status', filters.status);
    if (filters.priority) params.append('priority', filters.priority);
    if (filters.tags && filters.tags.length > 0) {
      filters.tags.forEach(tagId => params.append('tags', tagId.toString()));
    }
    if (filters.due_before) params.append('due_before', filters.due_before);
    if (filters.due_after) params.append('due_after', filters.due_after);
    if (filters.sort_by) params.append('sort_by', filters.sort_by);
    if (filters.sort_order) params.append('sort_order', filters.sort_order);
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.page_size) params.append('page_size', filters.page_size.toString());

    return params.toString();
  }, []);

  // Fetch tasks with current filters
  const fetchTasks = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const queryString = buildQueryString(filters);
      const url = queryString ? `${API_BASE}?${queryString}` : API_BASE;

      const response = await fetch(url, {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch tasks: ${response.statusText}`);
      }

      const data: TaskListResponse = await response.json();
      setTasks(data.items);
      setTotalCount(data.total_count);
      setPage(data.page);
      setTotalPages(data.total_pages);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tasks');
    } finally {
      setIsLoading(false);
    }
  }, [filters, buildQueryString]);

  // Fetch all tags
  const fetchTags = useCallback(async () => {
    try {
      const response = await fetch(TAGS_API, {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch tags: ${response.statusText}`);
      }

      const data: Tag[] = await response.json();
      setTags(data);
    } catch (err) {
      console.error('Failed to fetch tags:', err);
    }
  }, []);

  // Create a new task
  const createTask = useCallback(async (payload: TaskCreatePayload): Promise<Task> => {
    const response = await fetch(API_BASE, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Failed to create task: ${response.statusText}`);
    }

    const newTask: Task = await response.json();
    // Refresh tasks list
    await fetchTasks();
    return newTask;
  }, [fetchTasks]);

  // Update a task
  const updateTask = useCallback(async (id: number, payload: TaskUpdatePayload): Promise<Task> => {
    const response = await fetch(`${API_BASE}/${id}`, {
      method: 'PUT',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Failed to update task: ${response.statusText}`);
    }

    const updatedTask: Task = await response.json();
    // Update local state
    setTasks(prev => prev.map(t => t.id === id ? updatedTask : t));
    return updatedTask;
  }, []);

  // Delete a task
  const deleteTask = useCallback(async (id: number): Promise<void> => {
    const response = await fetch(`${API_BASE}/${id}`, {
      method: 'DELETE',
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`Failed to delete task: ${response.statusText}`);
    }

    // Remove from local state
    setTasks(prev => prev.filter(t => t.id !== id));
    setTotalCount(prev => prev - 1);
  }, []);

  // Complete a task
  const completeTask = useCallback(async (id: number): Promise<Task> => {
    const response = await fetch(`${API_BASE}/${id}/complete`, {
      method: 'PATCH',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to complete task: ${response.statusText}`);
    }

    const completedTask: Task = await response.json();
    setTasks(prev => prev.map(t => t.id === id ? completedTask : t));
    return completedTask;
  }, []);

  // Toggle task status
  const toggleTaskStatus = useCallback(async (id: number): Promise<Task> => {
    const response = await fetch(`${API_BASE}/${id}/toggle-status`, {
      method: 'PATCH',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to toggle task status: ${response.statusText}`);
    }

    const toggledTask: Task = await response.json();
    setTasks(prev => prev.map(t => t.id === id ? toggledTask : t));
    return toggledTask;
  }, []);

  // Create a new tag
  const createTag = useCallback(async (name: string): Promise<Tag> => {
    const response = await fetch(TAGS_API, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create tag: ${response.statusText}`);
    }

    const newTag: Tag = await response.json();
    setTags(prev => [...prev, newTag]);
    return newTag;
  }, []);

  // Delete a tag
  const deleteTag = useCallback(async (id: number): Promise<void> => {
    const response = await fetch(`${TAGS_API}/${id}`, {
      method: 'DELETE',
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`Failed to delete tag: ${response.statusText}`);
    }

    setTags(prev => prev.filter(t => t.id !== id));
  }, []);

  // Auto-fetch on mount and when filters change
  useEffect(() => {
    if (autoFetch) {
      fetchTasks();
    }
  }, [autoFetch, fetchTasks]);

  // Fetch tags on mount
  useEffect(() => {
    if (autoFetch) {
      fetchTags();
    }
  }, [autoFetch, fetchTags]);

  return {
    tasks,
    totalCount,
    page,
    totalPages,
    isLoading,
    error,
    filters,
    setFilters,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    completeTask,
    toggleTaskStatus,
    tags,
    fetchTags,
    createTag,
    deleteTag,
  };
}

export default useTasks;
