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
  remind_at?: string;  // T056: Reminder datetime
  recurrence_rule?: RecurrenceRule;
  recurrence_parent_id?: number;
  tags?: Tag[];
}

// T056: Task creation payload
export interface TaskCreatePayload {
  title: string;
  description?: string;
  priority?: TaskPriority;
  due_datetime?: string;
  remind_at?: string;
  recurrence_rule?: RecurrenceRule;
  tag_ids?: number[];
}

// T056: Task update payload
export interface TaskUpdatePayload {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_datetime?: string;
  remind_at?: string;
  recurrence_rule?: RecurrenceRule;
  tag_ids?: number[];
}

// T101: Paginated response
export interface TaskListResponse {
  items: Task[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// T102: Filter parameters
export interface TaskFilters {
  q?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  tags?: number[];
  due_before?: string;
  due_after?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  page?: number;
  page_size?: number;
}
