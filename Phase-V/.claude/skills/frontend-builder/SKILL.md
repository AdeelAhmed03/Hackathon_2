---
name: frontend-skill
description: Build modern Next.js pages, reusable components, responsive layouts, and styling with Tailwind CSS. Use for full-stack web application UI development.
---

# Frontend Skill – Build Pages, Components, Layout, Styling

## Instructions

1. **Next.js App Router Structure**
   - Use `app/` directory for routing
   - Create `page.tsx` for routes
   - Implement `layout.tsx` for shared UI
   - Use Server Components by default
   - Add `'use client'` only when needed (interactivity, hooks, browser APIs)

2. **Component Development**
   - Build reusable, typed TypeScript components
   - Implement proper props interfaces
   - Handle loading and error states
   - Create atomic, composable components
   - Use React hooks appropriately (useState, useEffect, useRef, etc.)

3. **Responsive Layout**
   - Mobile-first design approach
   - Use Tailwind breakpoints (`sm:`, `md:`, `lg:`, `xl:`, `2xl:`)
   - Implement flexbox and grid layouts
   - Ensure touch-friendly interactions
   - Test across viewport sizes

4. **Styling with Tailwind CSS**
   - Use utility-first classes
   - Maintain consistent spacing scale
   - Apply semantic color schemes
   - Implement dark mode support when needed
   - Keep accessibility in mind (contrast, focus states)

5. **Data Fetching Patterns**
   - Async Server Components for data fetching
   - Use `loading.tsx` for Suspense boundaries
   - Implement `error.tsx` for error handling
   - Client-side fetching with SWR or React Query when appropriate

## Best Practices

- **Performance**: Minimize client-side JavaScript, leverage Server Components
- **Accessibility**: Use semantic HTML, ARIA labels, keyboard navigation
- **Type Safety**: Define TypeScript interfaces for all props and data
- - **Code Organization**: Keep components focused and single-responsibility
- **Naming Conventions**: Use PascalCase for components, camelCase for functions
- **CSS Management**: Avoid inline styles, prefer Tailwind utilities
- **State Management**: Lift state up appropriately, use context sparingly
- **Error Boundaries**: Wrap components that might fail

## Example Structure
```typescript
// app/dashboard/page.tsx (Server Component)
import { UserStats } from '@/components/UserStats';
import { ActivityFeed } from '@/components/ActivityFeed';

async function getDashboardData() {
  const res = await fetch('https://api.example.com/dashboard');
  return res.json();
}

export default async function DashboardPage() {
  const data = await getDashboardData();
  
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          Dashboard
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <UserStats stats={data.stats} />
          <ActivityFeed activities={data.activities} />
        </div>
      </div>
    </div>
  );
}
```
```typescript
// components/UserStats.tsx (Server Component)
interface UserStatsProps {
  stats: {
    users: number;
    revenue: number;
    growth: number;
  };
}

export function UserStats({ stats }: UserStatsProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Statistics</h2>
      <div className="space-y-3">
        <div className="flex justify-between">
          <span className="text-gray-600">Total Users</span>
          <span className="font-bold">{stats.users}</span>
        </div>
        {/* More stats */}
      </div>
    </div>
  );
}
```
```typescript
// components/InteractiveButton.tsx (Client Component)
'use client';

import { useState } from 'react';

interface ButtonProps {
  label: string;
  onAction: () => void;
}

export function InteractiveButton({ label, onAction }: ButtonProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleClick = async () => {
    setIsLoading(true);
    await onAction();
    setIsLoading(false);
  };

  return (
    <button
      onClick={handleClick}
      disabled={isLoading}
      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 
                 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
    >
      {isLoading ? 'Loading...' : label}
    </button>
  );
}
```

## Common Patterns

### Layout Wrapper
```typescript
// app/layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <nav className="bg-white shadow">
          {/* Navigation */}
        </nav>
        <main>{children}</main>
        <footer className="bg-gray-800 text-white">
          {/* Footer */}
        </footer>
      </body>
    </html>
  );
}
```

### Responsive Grid
```typescript
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>
```

### Loading State
```typescript
// app/dashboard/loading.tsx
export default function Loading() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
    </div>
  );
}
```