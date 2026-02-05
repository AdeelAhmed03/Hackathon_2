/**
 * Chat types for AI Todo Chatbot (Phase III)
 */

// Message roles
export type MessageRole = 'user' | 'assistant' | 'tool';

// Single chat message
export interface ChatMessage {
  id?: number;
  role: MessageRole;
  content: string;
  toolCalls?: ToolCall[];
  toolResults?: ToolResult[];
  createdAt?: string;
}

// Tool call from assistant
export interface ToolCall {
  name: string;
  parameters: Record<string, unknown>;
}

// Tool execution result
export interface ToolResult {
  toolName: string;
  success: boolean;
  result: string;
}

// Chat request to API
export interface ChatRequest {
  message: string;
  conversationId?: number | null;
}

// Chat response from API
export interface ChatResponse {
  conversationId: number;
  message: {
    role: MessageRole;
    content: string;
  };
  toolExecuted: boolean;
  toolResults?: ToolResult[];
}

// Conversation summary (for list)
export interface ConversationSummary {
  id: number;
  title?: string | null;
  createdAt: string;
  updatedAt: string;
  messageCount?: number;
}

// Conversation with messages
export interface ConversationDetail {
  id: number;
  title?: string | null;
  createdAt: string;
  updatedAt: string;
  messages: ChatMessage[];
}

// Conversation list response
export interface ConversationListResponse {
  conversations: ConversationSummary[];
  total: number;
}

// Chat state for hook
export interface ChatState {
  messages: ChatMessage[];
  conversationId: number | null;
  isLoading: boolean;
  error: string | null;
}

// Chat actions for hook
export interface ChatActions {
  sendMessage: (content: string) => Promise<void>;
  loadConversation: (conversationId: number) => Promise<void>;
  startNewConversation: () => void;
  clearError: () => void;
}
