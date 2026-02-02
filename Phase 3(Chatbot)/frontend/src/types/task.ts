export enum TaskStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed'
}

export enum TaskPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high'
}

export enum RecurrenceRule {
  DAILY = 'daily',
  WEEKLY = 'weekly',
  MONTHLY = 'monthly',
  YEARLY = 'yearly'
}

export interface Tag {
  id: number;
  name: string;
  user_id: number;
}

export interface Task {
  id: number;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  owner_id: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  due_datetime?: string;
  recurrence_rule?: RecurrenceRule;
  recurrence_parent_id?: number;
  tags?: Tag[];
}
