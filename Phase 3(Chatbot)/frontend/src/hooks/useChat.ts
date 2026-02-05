'use client';

import { useState, useCallback, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import {
  ChatMessage,
  ChatRequest,
  ChatResponse,
  ChatState,
  ChatActions,
  ConversationDetail,
} from '@/types/chat';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://adeelahmed01-todo-chatbot.hf.space';

interface UseChatReturn extends ChatState, ChatActions {}

export function useChat(): UseChatReturn {
  const { session } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Start new conversation
  const startNewConversation = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  }, []);

  // Send message to chat API
  const sendMessage = useCallback(async (content: string) => {
    if (!session?.token) {
      setError('Please sign in to use the chat');
      return;
    }

    if (!content.trim()) {
      setError('Message cannot be empty');
      return;
    }

    setIsLoading(true);
    setError(null);

    // Add user message to UI immediately
    const userMessage: ChatMessage = {
      role: 'user',
      content: content.trim(),
      createdAt: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const request: ChatRequest = {
        message: content.trim(),
        conversationId: conversationId,
      };

      const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.token}`,
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        if (response.status === 401) {
          throw new Error('Session expired. Please sign in again.');
        } else if (response.status === 429) {
          throw new Error('Too many requests. Please wait a moment.');
        } else if (response.status === 503) {
          throw new Error('AI service is temporarily unavailable. Please try again later.');
        }

        throw new Error(errorData.detail || `Request failed: ${response.status}`);
      }

      const data: ChatResponse = await response.json();

      // Update conversation ID if new
      if (!conversationId && data.conversationId) {
        setConversationId(data.conversationId);
      }

      // Add assistant message
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: data.message.content,
        toolResults: data.toolResults,
        createdAt: new Date().toISOString(),
      };
      setMessages(prev => [...prev, assistantMessage]);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
      setError(errorMessage);

      // Remove the user message if request failed
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  }, [session?.token, conversationId]);

  // Load existing conversation
  const loadConversation = useCallback(async (convId: number) => {
    if (!session?.token) {
      setError('Please sign in to load conversations');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/chat/conversations/${convId}`,
        {
          headers: {
            'Authorization': `Bearer ${session.token}`,
          },
        }
      );

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Conversation not found');
        }
        throw new Error(`Failed to load conversation: ${response.status}`);
      }

      const data: ConversationDetail = await response.json();

      setConversationId(data.id);
      setMessages(data.messages.map(msg => ({
        id: msg.id,
        role: msg.role,
        content: msg.content || '',
        toolCalls: msg.toolCalls,
        toolResults: msg.toolResults,
        createdAt: msg.createdAt,
      })));

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load conversation';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [session?.token]);

  return {
    // State
    messages,
    conversationId,
    isLoading,
    error,
    // Actions
    sendMessage,
    loadConversation,
    startNewConversation,
    clearError,
  };
}

export default useChat;
