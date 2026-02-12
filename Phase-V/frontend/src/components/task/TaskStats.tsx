"use client";

import { useEffect, useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import { Task } from '@/types/task';
import { motion } from 'framer-motion';
import { CheckCircle2, Clock, AlertCircle, List } from 'lucide-react';

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
          'Authorization': `Bearer ${session?.token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        // Handle paginated response from backend
        const tasks: Task[] = data.items || data;

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

  const statItems = [
    { label: 'Total Tasks', value: stats.total, color: 'bg-primary/10 text-primary', icon: List },
    { label: 'Completed', value: stats.completed, color: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400', icon: CheckCircle2 },
    { label: 'Pending', value: stats.pending, color: 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400', icon: AlertCircle },
    { label: 'In Progress', value: stats.inProgress, color: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400', icon: Clock },
  ];

  return (
    <div className="bg-card rounded-xl shadow-sm border border-border p-6 sticky top-24">
      <h2 className="text-lg font-semibold mb-6 flex items-center">
        <div className="h-6 w-1 bg-primary rounded-full mr-3"></div>
        Statistics
      </h2>

      <div className="grid grid-cols-2 lg:grid-cols-1 gap-4">
        {statItems.map((item, index) => (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center p-3 rounded-lg hover:bg-accent/50 transition-colors"
          >
            <div className={`p-2 rounded-lg ${item.color} mr-4`}>
              <item.icon className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{item.label}</p>
              <p className="text-xl font-bold">{item.value}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {stats.total > 0 && (
        <div className="mt-6 pt-6 border-t border-border">
          <div className="flex justify-between items-end mb-2">
             <div className="text-sm text-muted-foreground">Completion Rate</div>
             <div className="text-lg font-bold text-primary">
                {Math.round((stats.completed / stats.total) * 100)}%
             </div>
          </div>
          <div className="w-full bg-secondary rounded-full h-2.5 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${(stats.completed / stats.total) * 100}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
              className="bg-primary h-2.5 rounded-full"
            ></motion.div>
          </div>
        </div>
      )}
    </div>
  );
}
