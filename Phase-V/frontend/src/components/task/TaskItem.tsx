"use client";

import { useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useNotification } from '@/contexts/NotificationContext';
import { Task, TaskPriority, TaskStatus, RecurrenceRule } from '@/types/task';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import { Check, X, Edit, Trash2, Calendar, Clock, Repeat, Bell, Tag } from 'lucide-react';

interface TaskItemProps {
  task: Task;
  onUpdate: (task: Task) => void;
  onDelete: (taskId: number) => void;
}

export default function TaskItem({ task, onUpdate, onDelete }: TaskItemProps) {
  const { session } = useAuth();
  const { showNotification } = useNotification();
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState(task.title);
  const [description, setDescription] = useState(task.description || '');
  const [priority, setPriority] = useState(task.priority);
  const [status, setStatus] = useState(task.status);
  const [dueDate, setDueDate] = useState(task.due_datetime ? task.due_datetime.slice(0, 16) : '');
  const [remindAt, setRemindAt] = useState(task.remind_at ? task.remind_at.slice(0, 16) : '');
  const [recurrenceRule, setRecurrenceRule] = useState<RecurrenceRule | ''>(task.recurrence_rule || '');

  const getPriorityColor = (p: TaskPriority) => {
    switch (p) {
      case TaskPriority.HIGH: return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
      case TaskPriority.MEDIUM: return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300';
      case TaskPriority.LOW: return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300';
    }
  };

  const getStatusColor = (s: TaskStatus) => {
    switch (s) {
      case TaskStatus.COMPLETED: return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
      case TaskStatus.IN_PROGRESS: return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300';
      case TaskStatus.PENDING: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300';
    }
  };

  const formatRelativeDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays < 0) return `${Math.abs(diffDays)}d overdue`;
    if (diffDays === 0) return 'Due today';
    if (diffDays === 1) return 'Due tomorrow';
    if (diffDays <= 7) return `Due in ${diffDays}d`;
    return date.toLocaleDateString();
  };

  const isDueOverdue = (dateStr: string) => {
    return new Date(dateStr) < new Date();
  };

  const handleSave = async () => {
    try {
      const payload: Record<string, unknown> = {
        title,
        description,
        status,
        priority,
      };

      if (dueDate) payload.due_datetime = new Date(dueDate).toISOString();
      else payload.due_datetime = null;
      if (remindAt) payload.remind_at = new Date(remindAt).toISOString();
      else payload.remind_at = null;
      payload.recurrence_rule = recurrenceRule || null;

      const response = await fetch(`/api/tasks/${task.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${session?.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const updatedTask = await response.json();
        onUpdate(updatedTask);
        setIsEditing(false);
        showNotification('Task updated successfully!', 'success');
      } else {
        const error = await response.json();
        showNotification(`Failed to update task: ${error.detail || 'Unknown error'}`, 'error');
      }
    } catch (error) {
      console.error('Error updating task:', error);
      showNotification('Error updating task', 'error');
    }
  };

  const handleToggleStatus = async () => {
    try {
      const response = await fetch(`/api/tasks/${task.id}/toggle-status`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${session?.token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const updatedTask = await response.json();
        onUpdate(updatedTask);
        showNotification(`Task ${updatedTask.status === 'completed' ? 'completed' : 'marked as pending'}!`, 'success');
      } else {
        const error = await response.json();
        showNotification(`Failed to update task status: ${error.detail || 'Unknown error'}`, 'error');
      }
    } catch (error) {
      console.error('Error toggling task status:', error);
      showNotification('Error updating task status', 'error');
    }
  };

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this task?')) {
      try {
        const response = await fetch(`/api/tasks/${task.id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${session?.token}`,
          },
        });

        if (response.ok) {
          onDelete(task.id);
          showNotification('Task deleted successfully!', 'success');
        } else {
          const error = await response.json();
          showNotification(`Failed to delete task: ${error.detail || 'Unknown error'}`, 'error');
        }
      } catch (error) {
        console.error('Error deleting task:', error);
        showNotification('Error deleting task', 'error');
      }
    }
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      whileHover={{ y: -2 }}
      className={`relative group bg-card p-4 rounded-xl border border-border transition-shadow hover:shadow-md ${task.status === TaskStatus.COMPLETED ? 'opacity-75' : ''}`}
    >
      {isEditing ? (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="input-field"
              autoFocus
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="input-field min-h-[80px]"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Priority</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value as TaskPriority)}
                className="input-field"
              >
                <option value={TaskPriority.LOW}>Low</option>
                <option value={TaskPriority.MEDIUM}>Medium</option>
                <option value={TaskPriority.HIGH}>High</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Status</label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as TaskStatus)}
                className="input-field"
              >
                <option value={TaskStatus.PENDING}>Pending</option>
                <option value={TaskStatus.IN_PROGRESS}>In Progress</option>
                <option value={TaskStatus.COMPLETED}>Completed</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Due Date</label>
              <input
                type="datetime-local"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Remind At</label>
              <input
                type="datetime-local"
                value={remindAt}
                onChange={(e) => setRemindAt(e.target.value)}
                className="input-field"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Recurring</label>
            <select
              value={recurrenceRule}
              onChange={(e) => setRecurrenceRule(e.target.value as RecurrenceRule | '')}
              className="input-field"
            >
              <option value="">None</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="yearly">Yearly</option>
            </select>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" size="sm" onClick={() => setIsEditing(false)}>
              Cancel
            </Button>
            <Button size="sm" onClick={handleSave}>
              Save Changes
            </Button>
          </div>
        </div>
      ) : (
        <div className="flex items-start gap-4">
          <div className="pt-1">
            <motion.button
              whileTap={{ scale: 0.8 }}
              onClick={handleToggleStatus}
              className={`flex items-center justify-center w-6 h-6 rounded border transition-colors ${
                task.status === TaskStatus.COMPLETED
                  ? 'bg-primary border-primary text-primary-foreground'
                  : 'bg-transparent border-gray-400 hover:border-primary'
              }`}
            >
              {task.status === TaskStatus.COMPLETED && <Check className="w-4 h-4" />}
            </motion.button>
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <h3 className={`font-medium text-lg leading-tight truncate pr-4 ${task.status === TaskStatus.COMPLETED ? 'text-muted-foreground/80 line-through' : 'text-foreground'}`}>
                {task.title}
              </h3>
              <div className="flex items-center gap-2 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground" onClick={() => setIsEditing(true)}>
                  <Edit className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive/80 hover:text-destructive hover:bg-destructive/10" onClick={handleDelete}>
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <p className={`mt-1 text-sm ${task.status === TaskStatus.COMPLETED ? 'text-muted-foreground/60' : 'text-muted-foreground'} line-clamp-2`}>
              {task.description}
            </p>

            {/* Tags */}
            {task.tags && task.tags.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {task.tags.map(tag => (
                  <span
                    key={tag.id}
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300"
                  >
                    <Tag className="h-3 w-3" />
                    {tag.name}
                  </span>
                ))}
              </div>
            )}

            <div className="mt-3 flex flex-wrap items-center gap-2">
              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getPriorityColor(task.priority)}`}>
                {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
              </span>
              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getStatusColor(task.status)}`}>
                {task.status.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
              </span>

              {/* Due Date */}
              {task.due_datetime && (
                <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${
                  isDueOverdue(task.due_datetime) && task.status !== TaskStatus.COMPLETED
                    ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                    : 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300'
                }`}>
                  <Clock className="h-3 w-3" />
                  {formatRelativeDate(task.due_datetime)}
                </span>
              )}

              {/* Recurring Badge */}
              {task.recurrence_rule && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                  <Repeat className="h-3 w-3" />
                  {task.recurrence_rule.charAt(0).toUpperCase() + task.recurrence_rule.slice(1)}
                </span>
              )}

              {/* Reminder Badge */}
              {task.remind_at && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300">
                  <Bell className="h-3 w-3" />
                  Reminder
                </span>
              )}

              <span className="text-xs text-muted-foreground flex items-center gap-1 ml-auto">
                <Calendar className="h-3 w-3" />
                {new Date(task.updated_at || task.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
}
