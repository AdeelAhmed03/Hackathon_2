'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { useNotification } from '@/contexts/NotificationContext';
import TaskItem from './TaskItem';
import TaskForm from './TaskForm';
import { Task } from '@/types/task';

export default function TaskList() {
  const { session } = useAuth();
  const { showNotification } = useNotification();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'in_progress' | 'completed'>('all');
  const [priorityFilter, setPriorityFilter] = useState<number | 'all'>('all');

  // Filter tasks based on selected filters
  const filteredTasks = tasks.filter(task => {
    const statusMatch = statusFilter === 'all' || task.status === statusFilter;
    const priorityMatch = priorityFilter === 'all' || task.priority === priorityFilter;
    return statusMatch && priorityMatch;
  });

  // Fetch tasks for the current user
  useEffect(() => {
    if (session?.user?.id) {
      fetchTasks();
    }
  }, [session]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/tasks`, {
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setTasks(data);
      } else {
        const error = await response.json();
        showNotification(`Failed to load tasks: ${error.detail || 'Unknown error'}`, 'error');
      }
    } catch (error) {
      console.error('Error fetching tasks:', error);
      showNotification('Error loading tasks', 'error');
    } finally {
      setLoading(false);
    }
  };

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

  if (loading) {
    return (
      <div className="text-center py-8">
        <p>Loading tasks...</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold">Your Tasks</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
        >
          {showForm ? 'Cancel' : 'Add Task'}
        </button>
      </div>

      <div className="flex flex-wrap gap-4 bg-gray-50 p-3 rounded-md mb-4 border border-gray-200">
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700">Status:</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as any)}
            className="text-sm p-1 border border-gray-300 rounded-md"
          >
            <option value="all">All</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
        </div>
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700">Priority:</label>
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value === 'all' ? 'all' : Number(e.target.value))}
            className="text-sm p-1 border border-gray-300 rounded-md"
          >
            <option value="all">All</option>
            <option value={1}>Low</option>
            <option value={2}>Medium-Low</option>
            <option value={3}>Medium</option>
            <option value={4}>Medium-High</option>
            <option value={5}>High</option>
          </select>
        </div>
      </div>

      {showForm && (
        <TaskForm
          onClose={() => setShowForm(false)}
          onTaskCreated={handleTaskCreated}
        />
      )}

      {filteredTasks.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          {tasks.length === 0 ? 'No tasks yet. Create your first task!' : 'No tasks match your filters.'}
        </div>
      ) : (
        <div className="space-y-3">
          {filteredTasks.map(task => (
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