export interface Task {
  id: number;
  title: string;
  description?: string;
  status: 'pending' | 'in_progress' | 'completed';
  priority: number; // 1 (low) to 5 (high)
  owner_id: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}