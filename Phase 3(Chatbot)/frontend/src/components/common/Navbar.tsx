"use client";

import { useAuth } from "@/lib/auth-context";
import { useTheme } from "next-themes";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, Sun, Moon, CheckSquare, LogOut, User, LayoutDashboard, ArrowRight, MessageSquare } from "lucide-react";

export default function Navbar() {
  const { user, signOut, isLoading } = useAuth();
  const { theme, setTheme, resolvedTheme } = useTheme();
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  // Avoid hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  const toggleMenu = () => setIsOpen(!isOpen);
  const closeMenu = () => setIsOpen(false);

  const toggleTheme = () => {
    setTheme(resolvedTheme === "dark" ? "light" : "dark");
  };

  const navLinks = [
    ...(user
      ? [
          { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
        ]
      : []),
  ];

  return (
    <nav className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2" onClick={closeMenu}>
              <motion.div
                initial={{ rotate: -10, scale: 0.9 }}
                animate={{ rotate: 0, scale: 1 }}
                transition={{ type: "spring", stiffness: 260, damping: 20 }}
                className="bg-primary text-primary-foreground p-1.5 rounded-md"
              >
                <CheckSquare className="h-6 w-6" />
              </motion.div>
              <span className="text-xl font-bold tracking-tight">TodoApp</span>
            </Link>
          </div>

          <div className="hidden md:block">
            <div className="flex items-center space-x-4">
              {navLinks.map((link) => (
                <Link
                  key={link.name}
                  href={link.href}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    pathname === link.href
                      ? "bg-secondary text-secondary-foreground"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  }`}
                >
                  {link.icon && <link.icon className="mr-2 h-4 w-4" />}
                  {link.name}
                </Link>
              ))}

              <div className="flex items-center space-x-2 ml-4 border-l pl-4 border-border">
                  <button
                    onClick={toggleTheme}
                    className="p-2 rounded-md text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
                    aria-label="Toggle theme"
                  >
                    {mounted && resolvedTheme === 'dark' ? (
                      <Sun className="h-5 w-5" />
                    ) : (
                      <Moon className="h-5 w-5" />
                    )}
                  </button>

                {!isLoading && (
                  user ? (
                    <div className="flex items-center space-x-4">
                      <div className="text-sm font-medium text-muted-foreground hidden lg:block">
                        {user.email}
                      </div>
                      <button
                        onClick={() => signOut()}
                        className="flex items-center text-sm font-medium text-destructive hover:text-destructive/80 transition-colors"
                      >
                        <LogOut className="mr-2 h-4 w-4" />
                        Sign Out
                      </button>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                       <Link
                        href="/sign-in"
                        className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors px-3 py-2"
                      >
                        Sign In
                      </Link>
                      <Link
                        href="/sign-up"
                        className="flex items-center bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2 rounded-md text-sm font-medium transition-colors shadow-sm"
                      >
                        Get Started
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Link>
                    </div>
                  )
                )}
              </div>
            </div>
          </div>

          <div className="flex md:hidden">
            <button
              onClick={toggleMenu}
              className="inline-flex items-center justify-center p-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary"
            >
              <span className="sr-only">Open main menu</span>
              {isOpen ? (
                <X className="block h-6 w-6" aria-hidden="true" />
              ) : (
                <Menu className="block h-6 w-6" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-b border-border bg-background"
          >
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
              {navLinks.map((link) => (
                <Link
                  key={link.name}
                  href={link.href}
                  className={`flex items-center px-3 py-2 rounded-md text-base font-medium ${
                    pathname === link.href
                      ? "bg-secondary text-secondary-foreground"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  }`}
                  onClick={closeMenu}
                >
                  {link.icon && <link.icon className="mr-2 h-5 w-5" />}
                  {link.name}
                </Link>
              ))}

              <div className="border-t border-border mt-4 pt-4 pb-2">
                 <div className="flex items-center justify-between px-3 py-2">
                    <span className="text-sm font-medium text-muted-foreground">Theme</span>
                    <button
                      onClick={toggleTheme}
                      className="p-2 rounded-md text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
                    >
                      {mounted && resolvedTheme === 'dark' ? (
                        <div className="flex items-center"><Sun className="h-5 w-5 mr-2" /> Light</div>
                      ) : (
                        <div className="flex items-center"><Moon className="h-5 w-5 mr-2" /> Dark</div>
                      )}
                    </button>
                 </div>

                {!isLoading && (
                  user ? (
                    <div className="space-y-1 mt-2">
                      <div className="px-3 py-2 text-sm font-medium text-muted-foreground">
                        {user.email}
                      </div>
                      <button
                        onClick={() => {
                          signOut();
                          closeMenu();
                        }}
                        className="w-full flex items-center px-3 py-2 text-base font-medium text-destructive hover:bg-destructive/10 rounded-md"
                      >
                        <LogOut className="mr-2 h-5 w-5" />
                        Sign Out
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-2 mt-2 px-3">
                       <Link
                        href="/sign-in"
                        className="block w-full text-center py-2 text-base font-medium text-muted-foreground hover:text-foreground border border-input rounded-md"
                        onClick={closeMenu}
                      >
                        Sign In
                      </Link>
                      <Link
                        href="/sign-up"
                        className="block w-full text-center py-2 text-base font-medium bg-primary text-primary-foreground rounded-md shadow-sm"
                        onClick={closeMenu}
                      >
                        Get Started
                      </Link>
                    </div>
                  )
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
