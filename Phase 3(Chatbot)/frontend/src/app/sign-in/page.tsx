'use client';

import { AuthProvider, useAuth } from '@/lib/auth';
import SignInForm from '@/components/auth/SignInForm';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

// Wrapper component to handle auth redirect
function SignInWrapper() {
  const { session } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // If user is already signed in, redirect to dashboard
    if (session) {
      router.push('/dashboard');
    }
  }, [session, router]);

  // Show sign in form if not authenticated
  if (session) {
    return null; // Redirecting...
  }

  return <SignInForm />;
}

export default function SignInPage() {
  return (
    <AuthProvider>
      <SignInWrapper />
    </AuthProvider>
  );
}