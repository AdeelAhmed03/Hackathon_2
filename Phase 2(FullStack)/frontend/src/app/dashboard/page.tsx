"use client";

import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import TaskList from "@/components/task/TaskList";
import TaskStats from "@/components/task/TaskStats";
import { motion } from "framer-motion";

export default function Dashboard() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/sign-in");
    }
  }, [user, isLoading, router]);

  if (isLoading) {
    return (
      <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center">
        <div className="text-lg text-muted-foreground animate-pulse">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-full py-8">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="md:flex md:items-center md:justify-between mb-8">
            <div className="min-w-0 flex-1">
              <h2 className="text-2xl font-bold leading-7 text-foreground sm:truncate sm:text-3xl sm:tracking-tight">
                Dashboard
              </h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Manage your tasks and track your progress.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* User Stats - Order switched for mobile (stats on top) or desktop (sidebar) */}
            <div className="lg:col-span-1 order-1 lg:order-2 space-y-6">
              <TaskStats />
            </div>

            {/* Tasks List */}
            <div className="lg:col-span-2 order-2 lg:order-1">
              <div className="bg-card shadow-sm border border-border rounded-xl overflow-hidden">
                <div className="px-6 py-5 border-b border-border bg-card/50">
                  <h3 className="text-lg font-medium leading-6 text-foreground">Your Tasks</h3>
                  <p className="mt-1 text-sm text-muted-foreground">
                    A list of all your current tasks and their status.
                  </p>
                </div>
                <div className="p-6">
                  <TaskList />
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
