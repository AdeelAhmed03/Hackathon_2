'use client';
import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';

interface NotificationProps {
  message: string;
  type?: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  onClose?: () => void;
}

export default function Notification({
  message,
  type = 'info',
  duration = 3000,
  onClose
}: NotificationProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        if (onClose) onClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  if (!isVisible) return null;

  const getTypeStyles = () => {
    switch (type) {
      case 'success':
        return 'bg-green-500 text-white';
      case 'error':
        return 'bg-red-500 text-white';
      case 'warning':
        return 'bg-yellow-500 text-black';
      case 'info':
      default:
        return 'bg-blue-500 text-white';
    }
  };

  return createPortal(
    <div className="fixed bottom-4 right-4 z-50">
      <div className={`${getTypeStyles()} px-4 py-2 rounded-md shadow-lg flex items-center space-x-2 animate-slide-in`}>
        <span>{message}</span>
        <button
          onClick={() => {
            setIsVisible(false);
            if (onClose) onClose();
          }}
          className="ml-2 text-white hover:text-gray-200 focus:outline-none"
        >
          ×
        </button>
      </div>
    </div>,
    document.body
  );
}