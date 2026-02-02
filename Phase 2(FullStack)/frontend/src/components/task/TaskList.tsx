'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useNotification } from '@/contexts/NotificationContext';
import TaskItem from './TaskItem';
import TaskForm from './TaskForm';
import { Task, TaskPriority, TaskStatus } from '@/types/task';
import { Button } from '@/components/ui/button';
import { Plus, X } from 'lucide-react';

export default function TaskList() {
  const { session } = useAuth();
  const { showNotification } = useNotification();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [statusFilter, setStatusFilter] = useState<'all' | TaskStatus>('all');
  const [priorityFilter, setPriorityFilter] = useState<'all' | TaskPriority>('all');

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
          'Authorization': `Bearer ${session?.token}`,
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
        <h2 className="text-lg font-semibold flex items-center gap-2">
          Your Tasks
          <span className="text-xs font-normal text-muted-foreground bg-secondary px-2 py-0.5 rounded-full">
            {filteredTasks.length}
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

      <div className="flex flex-wrap gap-4 bg-secondary/50 p-4 rounded-lg mb-6 border border-border">
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-foreground">Status:</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as any)}
            className="text-sm p-2 border border-input rounded-md bg-background text-foreground focus:ring-2 focus:ring-ring focus:outline-none"
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
            className="text-sm p-2 border border-input rounded-md bg-background text-foreground focus:ring-2 focus:ring-ring focus:outline-none"
          >
            <option value="all">All</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
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