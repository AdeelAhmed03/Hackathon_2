'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useChat } from '@/hooks/useChat';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { Bot, RotateCcw, Sparkles } from 'lucide-react';

interface ChatContainerProps {
  className?: string;
}

export function ChatContainer({ className = '' }: ChatContainerProps) {
  const {
    messages,
    conversationId,
    isLoading,
    error,
    sendMessage,
    startNewConversation,
    clearError,
  } = useChat();

  return (
    <div className={`flex flex-col h-full bg-gradient-to-b from-white to-gray-50 dark:from-gray-900 dark:to-gray-800 ${className}`}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between px-6 py-4 border-b dark:border-gray-700 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-700"
      >
        <div className="flex items-center gap-4">
          <div className="relative flex-shrink-0">
            <div className="w-12 h-12 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center text-white">
              <Bot className="w-6 h-6" />
            </div>
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white dark:border-gray-900"
            />
          </div>
          <div className="flex flex-col min-w-0">
            <h2 className="font-bold text-gray-900 dark:text-white text-lg leading-tight">
              AI Todo Assistant
            </h2>
            <div className="text-sm text-gray-600 dark:text-gray-400 flex items-center mt-1">
              <span className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2 flex-shrink-0" />
                <span>Online</span>
              </span>
              <span className="mx-2">•</span>
              <span className="truncate">{conversationId ? `Conversation #${conversationId}` : 'New conversation'}</span>
            </div>
          </div>
        </div>

        <motion.button
          onClick={startNewConversation}
          className="px-4 py-2 text-sm rounded-xl bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600 transition-all duration-200 flex items-center space-x-2 shadow-sm"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <RotateCcw className="w-4 h-4" />
          <span>New Chat</span>
        </motion.button>
      </motion.div>

      {/* Error banner */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="mx-4 mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl flex items-center justify-between shadow-md"
          >
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-red-600 dark:text-red-400" />
              </div>
              <span className="text-red-700 dark:text-red-400 text-sm">
                {error}
              </span>
            </div>
            <button
              onClick={clearError}
              className="text-red-500 hover:text-red-700 dark:hover:text-red-300 p-1 rounded-full hover:bg-red-200/30 transition-colors"
            >
              ✕
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Messages */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="flex-1 overflow-hidden"
      >
        <MessageList messages={messages} isLoading={isLoading} />
      </motion.div>

      {/* Input */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <MessageInput
          onSend={sendMessage}
          isLoading={isLoading}
        />
      </motion.div>
    </div>
  );
}

export default ChatContainer;
