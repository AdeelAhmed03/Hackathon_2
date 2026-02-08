'use client';

import { useAuth } from '@/lib/auth-context';
import SignInForm from '@/components/auth/SignInForm';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function SignInPage() {
  const { session, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // If user is already signed in, redirect to dashboard
    if (session) {
      router.push('/dashboard');
    }
  }, [session, router]);

  // Show loading state while checking auth
  if (isLoading) {
    return null;
  }

  // Show sign in form if not authenticated
  if (session) {
    return null; // Redirecting...
  }

  return <SignInForm />;
}