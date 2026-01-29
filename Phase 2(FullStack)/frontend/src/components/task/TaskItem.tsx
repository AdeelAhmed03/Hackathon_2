'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth';
import { useNotification } from '@/contexts/NotificationContext';
import { Task } from '@/types/task';

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

  const handleSave = async () => {
    try {
      const response = await fetch(`/api/tasks/${task.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title,
          description,
          status,
          priority,
        }),
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
          'Authorization': `Bearer ${session?.accessToken}`,
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
    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        const response = await fetch(`/api/tasks/${task.id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${session?.accessToken}`,
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

  const getStatusColor = () => {
    switch (task.status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'pending':
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = () => {
    switch (task.priority) {
      case 5:
        return 'text-red-600';
      case 4:
        return 'text-orange-600';
      case 3:
        return 'text-yellow-600';
      case 2:
        return 'text-blue-600';
      case 1:
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
      {isEditing ? (
        <div className="space-y-3">
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md"
            placeholder="Task title"
          />
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md"
            placeholder="Task description"
            rows={3}
          />
          <div className="flex space-x-3">
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value as any)}
              className="p-2 border border-gray-300 rounded-md"
            >
              <option value="pending">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
            </select>
            <select
              value={priority}
              onChange={(e) => setPriority(Number(e.target.value))}
              className="p-2 border border-gray-300 rounded-md"
            >
              <option value={1}>Low Priority</option>
              <option value={2}>Medium Priority</option>
              <option value={3}>High Priority</option>
              <option value={4}>Higher Priority</option>
              <option value={5}>Highest Priority</option>
            </select>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={handleSave}
              className="bg-green-600 text-white px-3 py-1 rounded-md hover:bg-green-700"
            >
              Save
            </button>
            <button
              onClick={() => setIsEditing(false)}
              className="bg-gray-600 text-white px-3 py-1 rounded-md hover:bg-gray-700"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-2">
          <div className="flex justify-between items-start">
            <h3 className={`font-medium ${task.status === 'completed' ? 'line-through text-gray-500' : ''}`}>
              {task.title}
            </h3>
            <div className="flex space-x-2">
              <button
                onClick={handleToggleStatus}
                className={`px-2 py-1 rounded text-xs ${
                  task.status === 'completed'
                    ? 'bg-gray-200 text-gray-700'
                    : 'bg-blue-100 text-blue-700'
                }`}
              >
                {task.status === 'completed' ? 'Undo' : 'Complete'}
              </button>
              <button
                onClick={() => setIsEditing(true)}
                className="text-blue-600 hover:text-blue-800 text-sm"
              >
                Edit
              </button>
              <button
                onClick={handleDelete}
                className="text-red-600 hover:text-red-800 text-sm"
              >
                Delete
              </button>
            </div>
          </div>

          {task.description && (
            <p className="text-gray-600 text-sm">{task.description}</p>
          )}

          <div className="flex justify-between items-center text-xs">
            <span className={`px-2 py-1 rounded-full ${getStatusColor()}`}>
              {task.status.replace('_', ' ')}
            </span>
            <span className={getPriorityColor()}>
              Priority: {task.priority}
            </span>
          </div>

          <div className="text-xs text-gray-500">
            Created: {new Date(task.created_at).toLocaleDateString()}
          </div>
        </div>
      )}
    </div>
  );
}