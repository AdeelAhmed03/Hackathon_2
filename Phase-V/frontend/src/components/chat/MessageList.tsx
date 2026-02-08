'use client';

import React, { useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChatMessage as ChatMessageType } from '@/types/chat';
import { ChatMessage } from './ChatMessage';
import { Sparkles, Lightbulb } from 'lucide-react';

interface MessageListProps {
  messages: ChatMessageType[];
  isLoading?: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto p-6 bg-gradient-to-b from-white/50 to-gray-50/50 dark:from-gray-900/30 dark:to-gray-800/30"
    >
      {/* Empty state */}
      {messages.length === 0 && !isLoading && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-center justify-center h-full text-gray-500 dark:text-gray-400"
        >
          <motion.div
            animate={{ rotate: [0, 10, -10, 0] }}
            transition={{ duration: 3, repeat: Infinity, repeatType: "reverse" }}
            className="text-8xl mb-6"
          >
            💬
          </motion.div>
          <motion.h3
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-2xl font-bold mb-2 text-gray-800 dark:text-gray-200"
          >
            Start a Conversation
          </motion.h3>
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-center max-w-md text-gray-600 dark:text-gray-400 mb-6"
          >
            Ask me to help manage your tasks! Try saying:
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-lg"
          >
            <SuggestionChip text="Add a task to buy groceries" />
            <SuggestionChip text="Show my tasks" />
            <SuggestionChip text="What's on my list?" />
            <SuggestionChip text="Mark buy milk as done" />
          </motion.div>
        </motion.div>
      )}

      {/* Messages with animation */}
      <AnimatePresence>
        {messages.map((message, index) => (
          <motion.div
            key={message.id || index}
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="mb-4"
          >
            <ChatMessage message={message} />
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Loading indicator */}
      {isLoading && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-start mb-4"
        >
          <div className="bg-gradient-to-r from-blue-100/50 to-purple-100/50 dark:from-blue-900/30 dark:to-purple-900/30 rounded-2xl px-5 py-4 shadow-sm border border-blue-200/30 dark:border-blue-800/30 backdrop-blur-sm">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <TypingIndicator />
            </div>
          </div>
        </motion.div>
      )}

      {/* Scroll anchor */}
      <div ref={bottomRef} />
    </div>
  );
}

// Suggestion chip component
function SuggestionChip({ text }: { text: string }) {
  return (
    <motion.div
      whileHover={{ scale: 1.03, y: -2 }}
      whileTap={{ scale: 0.98 }}
      className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 hover:from-blue-500/20 hover:to-purple-500/20 rounded-2xl px-4 py-3 text-gray-700 dark:text-gray-300 cursor-pointer border border-blue-200/30 dark:border-blue-800/30 transition-all duration-200 flex items-center space-x-2"
    >
      <Lightbulb className="w-4 h-4 flex-shrink-0" />
      <span className="text-sm font-medium">"{text}"</span>
    </motion.div>
  );
}

// Typing indicator component
function TypingIndicator() {
  return (
    <div className="flex items-center gap-2">
      <span className="text-gray-600 dark:text-gray-300 text-sm font-medium">
        Thinking
      </span>
      <div className="flex space-x-1">
        <motion.span
          className="w-2 h-2 bg-blue-500 rounded-full"
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
        />
        <motion.span
          className="w-2 h-2 bg-purple-500 rounded-full"
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
        />
        <motion.span
          className="w-2 h-2 bg-blue-500 rounded-full"
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
        />
      </div>
    </div>
  );
}

export default MessageList;
