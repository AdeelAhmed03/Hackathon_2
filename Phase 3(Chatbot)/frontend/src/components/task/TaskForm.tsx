'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useNotification } from '@/contexts/NotificationContext';
import { Task, TaskPriority } from '@/types/task';

interface TaskFormProps {
  onClose: () => void;
  onTaskCreated: (task: Task) => void;
}

export default function TaskForm({ onClose, onTaskCreated }: TaskFormProps) {
  const { session } = useAuth();
  const { showNotification } = useNotification();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<TaskPriority>(TaskPriority.MEDIUM);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session?.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title,
          description,
          priority,
        }),
      });

      if (response.ok) {
        const newTask = await response.json();
        onTaskCreated(newTask);
        setTitle('');
        setDescription('');
        setPriority(TaskPriority.MEDIUM);
        showNotification('Task created successfully!', 'success');
        onClose(); // Close the form after successful creation
      } else {
        const errorData = await response.json();
        // Handle Pydantic validation errors (array of error objects)
        const errorMessage = Array.isArray(errorData.detail)
          ? errorData.detail.map((e: { msg: string }) => e.msg).join(', ')
          : errorData.detail || 'Failed to create task';
        setError(errorMessage);
        showNotification(`Failed to create task: ${errorMessage}`, 'error');
      }
    } catch (err) {
      setError('An error occurred while creating the task');
      showNotification('Error creating task', 'error');
      console.error('Error creating task:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-card p-4 rounded-lg shadow-sm border border-border">
      <h3 className="text-lg font-medium mb-3 text-foreground">Create New Task</h3>

      {error && (
        <div className="mb-3 p-2 bg-destructive/10 text-destructive rounded text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-foreground mb-1">
            Title *
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="input-field"
            placeholder="Task title"
            disabled={isLoading}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-1">
            Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="input-field"
            placeholder="Task description (optional)"
            rows={3}
            disabled={isLoading}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-1">
            Priority
          </label>
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value as TaskPriority)}
            className="input-field"
            disabled={isLoading}
          >
            <option value="low">Low Priority</option>
            <option value="medium">Medium Priority</option>
            <option value="high">High Priority</option>
          </select>
        </div>

        <div className="flex space-x-2 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 btn-secondary"
            disabled={isLoading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className={`flex-1 btn-primary ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
            disabled={isLoading}
          >
            {isLoading ? 'Creating...' : 'Create Task'}
          </button>
        </div>
      </form>
    </div>
  );
}