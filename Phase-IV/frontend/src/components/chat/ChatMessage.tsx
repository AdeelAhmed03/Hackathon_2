'use client';

import React from 'react';
import { ChatMessage as ChatMessageType, ToolResult } from '@/types/chat';

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 shadow-sm ${
          isUser
            ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-700'
        }`}
      >
        {/* Message content */}
        <div className="whitespace-pre-wrap break-words leading-relaxed">
          {formatMessageContent(message.content)}
        </div>

        {/* Tool results (if any) */}
        {isAssistant && message.toolResults && message.toolResults.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <div className="text-xs text-gray-500 dark:text-gray-400 mb-2 font-medium">
              Actions performed:
            </div>
            <div className="flex flex-wrap gap-1.5">
              {message.toolResults.map((result, index) => (
                <ToolResultBadge key={index} result={result} />
              ))}
            </div>
          </div>
        )}

        {/* Timestamp */}
        {message.createdAt && (
          <div
            className={`text-xs mt-2 ${
              isUser ? 'text-blue-200' : 'text-gray-500 dark:text-gray-400'
            }`}
          >
            {formatTime(message.createdAt)}
          </div>
        )}
      </div>
    </div>
  );
}

// Tool result badge component
function ToolResultBadge({ result }: { result: ToolResult }) {
  const toolLabels: Record<string, string> = {
    add_task: 'Created task',
    list_tasks: 'Listed tasks',
    complete_task: 'Completed task',
    update_task: 'Updated task',
    delete_task: 'Deleted task',
  };

  const label = toolLabels[result.toolName] || result.toolName.replace(/_/g, ' ');

  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${
        result.success
          ? 'bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-300 dark:border-green-700'
          : 'bg-red-50 text-red-700 border-red-200 dark:bg-red-900/20 dark:text-red-300 dark:border-red-700'
      }`}
    >
      <span className="mr-1">{result.success ? '✓' : '✗'}</span>
      {label}
    </span>
  );
}

// Format message content with markdown-like styling
function formatMessageContent(content: string): React.ReactNode {
  if (!content) return null;

  // Split by newlines and process each line
  const lines = content.split('\n');

  return lines.map((line, index) => {
    // Bold text with **
    let formattedLine: React.ReactNode = line;

    // Simple bold replacement
    if (line.includes('**')) {
      const parts = line.split(/\*\*(.*?)\*\*/g);
      formattedLine = parts.map((part, i) =>
        i % 2 === 1 ? <strong key={i}>{part}</strong> : part
      );
    }

    return (
      <React.Fragment key={index}>
        {formattedLine}
        {index < lines.length - 1 && <br />}
      </React.Fragment>
    );
  });
}

// Format timestamp
function formatTime(dateString: string): string {
  try {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch {
    return '';
  }
}

export default ChatMessage;
