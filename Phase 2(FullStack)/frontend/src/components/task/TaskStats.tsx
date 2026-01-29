import { useEffect, useState } from 'react';
import { useAuth } from '@/lib/auth';
import { Task } from '@/types/task';

export default function TaskStats() {
  const { session } = useAuth();
  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    pending: 0,
    inProgress: 0,
  });

  useEffect(() => {
    if (session?.user?.id) {
      fetchStats();
    }
  }, [session]);

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/tasks', {
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const tasks: Task[] = await response.json();

        const total = tasks.length;
        const completed = tasks.filter(t => t.status === 'completed').length;
        const pending = tasks.filter(t => t.status === 'pending').length;
        const inProgress = tasks.filter(t => t.status === 'in_progress').length;

        setStats({
          total,
          completed,
          pending,
          inProgress,
        });
      }
    } catch (error) {
      console.error('Error fetching task stats:', error);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
      <h2 className="text-lg font-semibold mb-4">Statistics</h2>
      <div className="space-y-4">
        <div className="flex justify-between">
          <span className="text-gray-600">Total Tasks</span>
          <span className="font-medium">{stats.total}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Completed</span>
          <span className="font-medium text-green-600">{stats.completed}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Pending</span>
          <span className="font-medium text-red-600">{stats.pending}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">In Progress</span>
          <span className="font-medium text-yellow-600">{stats.inProgress}</span>
        </div>

        {stats.total > 0 && (
          <div className="pt-4 border-t border-gray-200">
            <div className="text-sm text-gray-600 mb-1">Completion Rate</div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-600 h-2 rounded-full"
                style={{
                  width: `${stats.total > 0 ? (stats.completed / stats.total) * 100 : 0}%`
                }}
              ></div>
            </div>
            <div className="text-right text-sm text-gray-600 mt-1">
              {stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0}%
            </div>
          </div>
        )}
      </div>
    </div>
  );
}