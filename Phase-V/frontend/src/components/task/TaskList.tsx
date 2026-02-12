'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useNotification } from '@/contexts/NotificationContext';
import TaskItem from './TaskItem';
import TaskForm from './TaskForm';
import { Task, TaskPriority, TaskStatus } from '@/types/task';
import { Button } from '@/components/ui/button';
import { Plus, X, Search, ArrowUpDown } from 'lucide-react';

export default function TaskList() {
  const { session } = useAuth();
  const { showNotification } = useNotification();
  const notifyRef = useRef(showNotification);
  notifyRef.current = showNotification;
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  // Filter & search state
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | TaskStatus>('all');
  const [priorityFilter, setPriorityFilter] = useState<'all' | TaskPriority>('all');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [debouncedQuery, setDebouncedQuery] = useState('');

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(searchQuery), 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Fetch tasks with server-side params
  const fetchTasks = useCallback(async () => {
    if (!session?.user?.id) return;
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (debouncedQuery) params.set('q', debouncedQuery);
      if (statusFilter !== 'all') params.set('status', statusFilter);
      if (priorityFilter !== 'all') params.set('priority', priorityFilter);
      params.set('sort_by', sortBy);
      params.set('sort_order', sortOrder);
      params.set('page_size', '100');

      const qs = params.toString();
      const response = await fetch(`/api/tasks${qs ? `?${qs}` : ''}`, {
        headers: {
          'Authorization': `Bearer ${session?.token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setTasks(data.items || data);
      } else {
        const error = await response.json();
        notifyRef.current(`Failed to load tasks: ${error.detail || 'Unknown error'}`, 'error');
      }
    } catch (error) {
      console.error('Error fetching tasks:', error);
      notifyRef.current('Error loading tasks', 'error');
    } finally {
      setLoading(false);
    }
  }, [session?.user?.id, session?.token, debouncedQuery, statusFilter, priorityFilter, sortBy, sortOrder]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleTaskCreated = (newTask: Task) => {
    setTasks(prev => [newTask, ...prev]);
    setShowForm(false);
    showNotification('Task created successfully!', 'success');
  };

  const handleTaskUpdated = (updatedTask: Task) => {
    setTasks(prev => prev.map(task => task.id === updatedTask.id ? updatedTask : task));
    showNotification('Task updated successfully!', 'success');
  };

  const handleTaskDeleted = (taskId: number) => {
    setTasks(prev => prev.filter(task => task.id !== taskId));
    showNotification('Task deleted successfully!', 'success');
  };

  if (loading && tasks.length === 0) {
    return (
      <div className="text-center py-8">
        <p>Loading tasks...</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          Your Tasks
          <span className="text-xs font-normal text-muted-foreground bg-secondary px-2 py-0.5 rounded-full">
            {tasks.length}
          </span>
        </h2>
        <Button
          onClick={() => setShowForm(!showForm)}
          variant={showForm ? "outline" : "default"}
          size="sm"
          className="gap-2"
        >
          {showForm ? (
            <>
              <X className="h-4 w-4" /> Cancel
            </>
          ) : (
            <>
              <Plus className="h-4 w-4" /> Add Task
            </>
          )}
        </Button>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search tasks..."
          className="input-field pl-10 w-full"
        />
      </div>

      {/* Filters & Sort */}
      <div className="flex flex-wrap gap-3 bg-secondary/50 p-3 rounded-lg border border-border">
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-foreground">Status:</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as 'all' | TaskStatus)}
            className="text-sm p-1.5 border border-input rounded-md bg-background text-foreground focus:ring-2 focus:ring-ring focus:outline-none"
          >
            <option value="all">All</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
        </div>
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-foreground">Priority:</label>
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value as 'all' | TaskPriority)}
            className="text-sm p-1.5 border border-input rounded-md bg-background text-foreground focus:ring-2 focus:ring-ring focus:outline-none"
          >
            <option value="all">All</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-foreground">Sort:</label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="text-sm p-1.5 border border-input rounded-md bg-background text-foreground focus:ring-2 focus:ring-ring focus:outline-none"
          >
            <option value="created_at">Date Created</option>
            <option value="due_datetime">Due Date</option>
            <option value="priority">Priority</option>
            <option value="title">Title</option>
          </select>
          <button
            onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
            className="p-1.5 border border-input rounded-md bg-background hover:bg-secondary transition-colors"
            title={`Sort ${sortOrder === 'asc' ? 'descending' : 'ascending'}`}
          >
            <ArrowUpDown className="h-4 w-4 text-foreground" />
          </button>
        </div>
      </div>

      {showForm && (
        <TaskForm
          onClose={() => setShowForm(false)}
          onTaskCreated={handleTaskCreated}
        />
      )}

      {tasks.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          {debouncedQuery || statusFilter !== 'all' || priorityFilter !== 'all'
            ? 'No tasks match your filters.'
            : 'No tasks yet. Create your first task!'}
        </div>
      ) : (
        <div className="space-y-3">
          {tasks.map(task => (
            <TaskItem
              key={task.id}
              task={task}
              onUpdate={handleTaskUpdated}
              onDelete={handleTaskDeleted}
            />
          ))}
        </div>
      )}
    </div>
  );
}
