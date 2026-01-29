'use client';

import { AuthProvider, useAuth } from '@/lib/auth';
import SignUpForm from '@/components/auth/SignUpForm';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

// Wrapper component to handle auth redirect
function SignUpWrapper() {
  const { session } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // If user is already signed in, redirect to dashboard
    if (session) {
      router.push('/dashboard');
    }
  }, [session, router]);

  // Show sign up form if not authenticated
  if (session) {
    return null; // Redirecting...
  }

  return <SignUpForm />;
}

export default function SignUpPage() {
  return (
    <AuthProvider>
      <SignUpWrapper />
    </AuthProvider>
  );
}