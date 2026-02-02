"use client";

import { useAuth } from "@/lib/auth-context";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, CheckSquare, Layers, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Home() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center">
        <div className="text-lg text-muted-foreground animate-pulse">Loading...</div>
      </div>
    );
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.3
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
  };

  return (
    <div className="flex flex-col min-h-[calc(100vh-4rem)]">
      {/* Hero Section */}
      <section className="flex-1 flex items-center justify-center py-12 md:py-24 lg:py-32 xl:py-48 px-4 md:px-6">
        <motion.div
          initial="hidden"
          animate="visible"
          variants={containerVariants}
          className="container px-4 md:px-6 flex flex-col items-center text-center space-y-4"
        >
          <motion.div variants={itemVariants} className="space-y-2">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tighter text-foreground">
              Master Your Day with <span className="text-primary">TodoApp</span>
            </h1>
            <p className="mx-auto max-w-[700px] text-muted-foreground md:text-xl lg:text-xl">
              A modern, powerful, and simpler way to manage your tasks.
              Organize your life, boost productivity, and get things done.
            </p>
          </motion.div>

          <motion.div variants={itemVariants} className="flex flex-col sm:flex-row gap-4 min-w-[300px] justify-center pt-4">
            {user ? (
              <Link href="/dashboard">
                <div className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-md px-8 py-3 text-lg font-medium flex items-center justify-center transition-colors shadow-lg shadow-primary/25 cursor-pointer">
                  Go to Dashboard
                  <ArrowRight className="ml-2 h-5 w-5" />
                </div>
              </Link>
            ) : (
              <>
                <Link href="/sign-up">
                  <div className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-md px-8 py-3 text-lg font-medium flex items-center justify-center transition-colors shadow-lg shadow-primary/25 cursor-pointer">
                    Get Started
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </div>
                </Link>
                <Link href="/sign-in">
                  <div className="bg-secondary text-secondary-foreground hover:bg-secondary/80 rounded-md px-8 py-3 text-lg font-medium flex items-center justify-center transition-colors cursor-pointer border border-border">
                    Sign In
                  </div>
                </Link>
              </>
            )}
          </motion.div>

          <motion.div
            variants={itemVariants}
            className="pt-12 grid grid-cols-1 md:grid-cols-3 gap-8 text-left max-w-5xl mx-auto w-full"
          >
            <div className="flex flex-col space-y-2 p-6 rounded-xl border border-border bg-card shadow-sm hover:shadow-md transition-shadow">
              <div className="p-2 w-fit rounded-lg bg-primary/10 text-primary">
                <CheckSquare className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">Stay Organized</h3>
              <p className="text-muted-foreground">Keep all your tasks in one place. Categorize update, and track progress effortlessly.</p>
            </div>

            <div className="flex flex-col space-y-2 p-6 rounded-xl border border-border bg-card shadow-sm hover:shadow-md transition-shadow">
              <div className="p-2 w-fit rounded-lg bg-primary/10 text-primary">
                <Zap className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">Boost Productivity</h3>
              <p className="text-muted-foreground">Focus on what matters most with priority levels and due dates to never miss a deadline.</p>
            </div>

            <div className="flex flex-col space-y-2 p-6 rounded-xl border border-border bg-card shadow-sm hover:shadow-md transition-shadow">
              <div className="p-2 w-fit rounded-lg bg-primary/10 text-primary">
                <Layers className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">Simple Workflow</h3>
              <p className="text-muted-foreground">A clean, intuitive interface designed to get out of your way and let you work.</p>
            </div>
          </motion.div>
        </motion.div>
      </section>
    </div>
  );
}
