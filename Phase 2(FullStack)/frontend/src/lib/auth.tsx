'use client';

import { createAuthClient } from 'better-auth/react';
import { createContext, useContext, useEffect, useState } from 'react';

// Initialize Better Auth client
const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000',
  fetch: globalThis.fetch,
});

// Create auth context
const AuthContext = createContext<any>(undefined);

// Auth provider component
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<any>(undefined);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Get current session on component mount
    const getSession = async () => {
      try {
        const result = await authClient.getSession() as any;
        setSession(result?.data?.session || null);
      } catch (error) {
        console.error('Error getting session:', error);
        setSession(null);
      } finally {
        setIsLoading(false);
      }
    };

    getSession();

    // Listen for session changes
    const unsubscribe = (authClient as any).subscribe((event: any) => {
      if (event.event === 'SESSION_UPDATED') {
        setSession(event.data.session);
      } else if (event.event === 'SIGN_OUT') {
        setSession(null);
      }
    });

    return () => unsubscribe();
  }, []);

  const value = {
    session,
    isLoading,
    signIn: authClient.signIn,
    signOut: authClient.signOut,
    signUp: authClient.signUp,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Custom hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default authClient;