'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, Send, Bot, Minimize2 } from 'lucide-react';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { useChat } from '@/hooks/useChat';

const FloatingChatButton = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [isVisible, setIsVisible] = useState(true);
  const pathname = usePathname();
  const { user } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { messages, isLoading, error, sendMessage, clearError, startNewConversation } = useChat();

  // Hide the chat button on the chat page itself
  useEffect(() => {
    setIsVisible(pathname !== '/chat');
  }, [pathname]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (isOpen && !isMinimized) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen, isMinimized]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const message = inputValue.trim();
    setInputValue('');
    await sendMessage(message);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isVisible || !user) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            transition={{ type: 'spring', stiffness: 300, damping: 25 }}
            className="mb-4 bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden"
            style={{
              width: isMinimized ? '320px' : '400px',
              height: isMinimized ? 'auto' : '600px',
              maxHeight: '80vh'
            }}
          >
            {/* Chat Header */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-4 text-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0">
                    <Bot className="w-5 h-5" />
                  </div>
                  <div className="flex flex-col">
                    <h3 className="font-semibold text-sm leading-tight">AI Assistant</h3>
                    <div className="flex items-center space-x-1 mt-0.5">
                      <div className="w-1.5 h-1.5 bg-green-400 rounded-full" />
                      <span className="text-xs text-blue-100">Online</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-1 flex-shrink-0">
                  <button
                    onClick={() => setIsMinimized(!isMinimized)}
                    className="p-2 hover:bg-white/20 rounded-full transition-colors"
                    title={isMinimized ? "Expand" : "Minimize"}
                  >
                    <Minimize2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setIsOpen(false)}
                    className="p-2 hover:bg-white/20 rounded-full transition-colors"
                    title="Close"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            {/* Chat Body - Only show when not minimized */}
            {!isMinimized && (
              <>
                {/* Messages Area */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ height: 'calc(100% - 140px)' }}>
                  {/* Welcome message when empty */}
                  {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-center px-4">
                      <div className="text-6xl mb-4">💬</div>
                      <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
                        Start a Conversation
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                        Ask me to help manage your tasks!
                      </p>
                      <div className="space-y-2 w-full max-w-xs">
                        {[
                          "Add a task to buy groceries",
                          "Show my tasks",
                          "Mark buy milk as done"
                        ].map((suggestion, idx) => (
                          <button
                            key={idx}
                            onClick={() => setInputValue(suggestion)}
                            className="w-full text-left px-3 py-2.5 text-xs bg-gradient-to-r from-blue-50 to-purple-50 hover:from-blue-100 hover:to-purple-100 dark:from-blue-900/20 dark:to-purple-900/20 dark:hover:from-blue-900/30 dark:hover:to-purple-900/30 text-gray-700 dark:text-gray-300 rounded-lg transition-all duration-200 border border-blue-200/30 dark:border-blue-800/30"
                          >
                            💡 "{suggestion}"
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Messages */}
                  {messages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}
                    >
                      <div
                        className={`max-w-[85%] rounded-2xl px-4 py-3 shadow-sm ${
                          message.role === 'user'
                            ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-600'
                        }`}
                      >
                        <div className="text-sm whitespace-pre-wrap break-words leading-relaxed">{message.content}</div>
                        {message.toolResults && message.toolResults.length > 0 && (
                          <div className="mt-2.5 pt-2.5 border-t border-white/20 dark:border-gray-600">
                            <div className="flex flex-wrap gap-1">
                              {message.toolResults.map((result, idx) => (
                                <span
                                  key={idx}
                                  className={`inline-flex items-center text-xs px-2 py-1 rounded-full font-medium ${
                                    result.success
                                      ? 'bg-green-500/20 text-green-200 border border-green-400/30'
                                      : 'bg-red-500/20 text-red-200 border border-red-400/30'
                                  }`}
                                >
                                  <span className="mr-1">{result.success ? '✓' : '✗'}</span>
                                  {result.toolName.replace(/_/g, ' ')}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}

                  {/* Loading indicator */}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl px-4 py-3">
                        <div className="flex items-center space-x-2">
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
                          <span className="text-xs text-gray-600 dark:text-gray-400">Thinking...</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Error message */}
                  {error && (
                    <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-3 shadow-sm">
                      <div className="flex items-start space-x-2">
                        <span className="text-red-500 text-sm flex-shrink-0">⚠️</span>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-red-800 dark:text-red-200 leading-snug">{error}</p>
                          <button
                            onClick={clearError}
                            className="text-xs text-red-600 dark:text-red-400 hover:underline mt-1.5 font-medium"
                          >
                            Dismiss
                          </button>
                        </div>
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="border-t border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-800">
                  <div className="flex items-end space-x-2">
                    <input
                      type="text"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Type your message..."
                      disabled={isLoading}
                      className="flex-1 px-4 py-2.5 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 text-sm placeholder-gray-400 dark:placeholder-gray-500 transition-shadow"
                    />
                    <button
                      onClick={handleSendMessage}
                      disabled={!inputValue.trim() || isLoading}
                      className="p-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-sm hover:shadow-md flex-shrink-0"
                      title="Send message"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                  {messages.length > 0 && (
                    <button
                      onClick={startNewConversation}
                      className="mt-2.5 text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 font-medium transition-colors"
                    >
                      🔄 Start new conversation
                    </button>
                  )}
                </div>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Button */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className="w-14 h-14 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center relative overflow-hidden group"
        whileHover={{ scale: 1.05, boxShadow: '0 10px 30px rgba(59, 130, 246, 0.4)' }}
        whileTap={{ scale: 0.95 }}
      >
        {/* Animated background effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

        {/* Icon */}
        <motion.div
          animate={{ rotate: isOpen ? 45 : 0 }}
          transition={{ duration: 0.2 }}
        >
          {isOpen ? <X className="w-6 h-6" /> : <MessageCircle className="w-6 h-6" />}
        </motion.div>

        {/* Pulse animation for online indicator */}
        {!isOpen && (
          <motion.div
            className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white dark:border-gray-900"
            animate={{
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        )}
      </motion.button>
    </div>
  );
};

export default FloatingChatButton;
