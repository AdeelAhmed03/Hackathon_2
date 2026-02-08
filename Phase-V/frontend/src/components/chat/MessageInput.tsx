'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send, Sparkles } from 'lucide-react';

interface MessageInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  disabled?: boolean;
  placeholder?: string;
}

export function MessageInput({
  onSend,
  isLoading,
  disabled = false,
  placeholder = 'Type a message... (e.g., "Add task buy groceries")',
}: MessageInputProps) {
  const [input, setInput] = useState('');
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-focus on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = inputRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
    }
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();

    if (!input.trim() || isLoading || disabled) return;

    onSend(input.trim());
    setInput('');

    // Reset textarea height
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <motion.form
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-end gap-3 p-4 border-t dark:border-gray-700 bg-white dark:bg-gray-900/50 backdrop-blur-sm"
    >
      <div className="flex-1 relative">
        <div className="relative">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={isLoading || disabled}
            rows={1}
            className={`
              w-full px-5 py-4 pr-12 rounded-2xl border
              dark:bg-gray-800/70 dark:border-gray-600 dark:text-white
              focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500
              resize-none overflow-hidden
              transition-all duration-200
              ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white shadow-sm hover:shadow-md'}
            `}
            style={{ minHeight: '56px', maxHeight: '150px' }}
          />
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            <Sparkles className="w-4 h-4" />
          </div>
        </div>
      </div>

      <motion.button
        type="submit"
        disabled={!input.trim() || isLoading || disabled}
        className={`
          px-5 py-4 rounded-2xl font-medium
          transition-all duration-200
          flex items-center justify-center
          shadow-lg
          ${
            !input.trim() || isLoading || disabled
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 shadow-blue-500/25 hover:shadow-blue-500/40'
          }
        `}
        whileHover={!input.trim() && !isLoading && !disabled ? { scale: 1.05 } : {}}
        whileTap={!input.trim() && !isLoading && !disabled ? { scale: 0.95 } : {}}
      >
        {isLoading ? (
          <motion.span
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
          </motion.span>
        ) : (
          <motion.div
            whileHover={{ x: 2 }}
            transition={{ type: "spring", stiffness: 400, damping: 17 }}
          >
            <Send className="w-4 h-4" />
          </motion.div>
        )}
      </motion.button>
    </motion.form>
  );
}

export default MessageInput;
