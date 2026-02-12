'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useNotification } from '@/contexts/NotificationContext';
import { Task, TaskPriority, RecurrenceRule, Tag } from '@/types/task';

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
  const [dueDate, setDueDate] = useState('');
  const [remindAt, setRemindAt] = useState('');
  const [recurrenceRule, setRecurrenceRule] = useState<RecurrenceRule | ''>('');
  const [availableTags, setAvailableTags] = useState<Tag[]>([]);
  const [selectedTagIds, setSelectedTagIds] = useState<number[]>([]);
  const [newTagName, setNewTagName] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Fetch available tags
  useEffect(() => {
    if (session?.token) {
      fetch('/api/tags', {
        headers: { 'Authorization': `Bearer ${session.token}` },
      })
        .then(res => res.json())
        .then(data => setAvailableTags(Array.isArray(data) ? data : []))
        .catch(() => {});
    }
  }, [session?.token]);

  const handleCreateTag = async () => {
    if (!newTagName.trim()) return;
    try {
      const res = await fetch('/api/tags', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session?.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: newTagName.trim() }),
      });
      if (res.ok) {
        const tag = await res.json();
        setAvailableTags(prev => [...prev, tag]);
        setSelectedTagIds(prev => [...prev, tag.id]);
        setNewTagName('');
      }
    } catch {}
  };

  const toggleTag = (tagId: number) => {
    setSelectedTagIds(prev =>
      prev.includes(tagId)
        ? prev.filter(id => id !== tagId)
        : [...prev, tagId]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const payload: Record<string, unknown> = {
        title,
        description: description || undefined,
        priority,
      };

      if (dueDate) payload.due_datetime = new Date(dueDate).toISOString();
      if (remindAt) payload.remind_at = new Date(remindAt).toISOString();
      if (recurrenceRule) payload.recurrence_rule = recurrenceRule;
      if (selectedTagIds.length > 0) payload.tag_ids = selectedTagIds;

      const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session?.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const newTask = await response.json();
        onTaskCreated(newTask);
        showNotification('Task created successfully!', 'success');
        onClose();
      } else {
        const errorData = await response.json();
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

        <div className="grid grid-cols-2 gap-4">
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
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Due Date
            </label>
            <input
              type="datetime-local"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              className="input-field"
              disabled={isLoading}
            />
          </div>
        </div>

        {/* Advanced options toggle */}
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-sm text-primary hover:underline"
        >
          {showAdvanced ? 'Hide advanced options' : 'Show advanced options (tags, recurring, reminder)'}
        </button>

        {showAdvanced && (
          <div className="space-y-4 border-t border-border pt-4">
            {/* Recurrence Rule */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Recurring
              </label>
              <select
                value={recurrenceRule}
                onChange={(e) => setRecurrenceRule(e.target.value as RecurrenceRule | '')}
                className="input-field"
                disabled={isLoading}
              >
                <option value="">None</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
              </select>
            </div>

            {/* Reminder */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Remind At
              </label>
              <input
                type="datetime-local"
                value={remindAt}
                onChange={(e) => setRemindAt(e.target.value)}
                className="input-field"
                disabled={isLoading}
              />
            </div>

            {/* Tags */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Tags
              </label>
              <div className="flex flex-wrap gap-2 mb-2">
                {availableTags.map(tag => (
                  <button
                    key={tag.id}
                    type="button"
                    onClick={() => toggleTag(tag.id)}
                    className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                      selectedTagIds.includes(tag.id)
                        ? 'bg-primary text-primary-foreground border-primary'
                        : 'bg-secondary text-secondary-foreground border-border hover:border-primary'
                    }`}
                  >
                    {tag.name}
                  </button>
                ))}
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newTagName}
                  onChange={(e) => setNewTagName(e.target.value)}
                  placeholder="New tag name"
                  className="input-field flex-1 text-sm"
                  onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleCreateTag(); } }}
                />
                <button
                  type="button"
                  onClick={handleCreateTag}
                  className="px-3 py-1 bg-secondary text-secondary-foreground rounded text-sm hover:bg-secondary/80"
                >
                  Add
                </button>
              </div>
            </div>
          </div>
        )}

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
