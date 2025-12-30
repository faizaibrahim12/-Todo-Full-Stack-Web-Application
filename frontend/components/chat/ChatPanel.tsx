'use client';

import { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { api } from '@/lib/api';
import type { ChatMessage, ChatResponse } from '@/lib/types';

interface ChatPanelProps {
  onTaskChange?: () => void;
  
}

interface MessageItem {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function ChatPanel({ onTaskChange }: ChatPanelProps) {
  const { user } = useAuth();
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !user || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);

    // Add user message immediately
    const tempId = Date.now().toString();
    setMessages(prev => [
      ...prev,
      {
        id: tempId,
        role: 'user',
        content: userMessage,
        timestamp: new Date(),
      },
    ]);

    try {
      const response = await api.chat(user.id, {
        message: userMessage,
        conversation_id: conversationId || undefined,
      });

      // Replace temp message with actual and add assistant response
      setMessages(prev => {
        const withoutTemp = prev.filter(m => m.id !== tempId);
        return [
          ...withoutTemp,
          {
            id: tempId,
            role: 'user',
            content: userMessage,
            timestamp: new Date(),
          },
          {
            id: response.conversation_id + '-' + Date.now(),
            role: 'assistant',
            content: response.response,
            timestamp: new Date(),
          },
        ];
      });

      setConversationId(response.conversation_id);

      // Trigger task refresh if actions were performed
      if (response.actions.length > 0 && onTaskChange) {
        onTaskChange();
      }
    } catch (error) {
      // Add error message
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
      setMessages(prev => [
        ...prev,
        {
          id: tempId + '-error',
          role: 'assistant',
          content: `Error: ${errorMessage}`,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-md">
      {/* Header */}
      <div className="px-4 py-3 border-b bg-gray-50 rounded-t-lg">
        <h2 className="text-lg font-semibold text-gray-800">AI Todo Assistant</h2>
        <p className="text-sm text-gray-500">Manage tasks with natural language</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <svg
              className="w-12 h-12 mb-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
              />
            </svg>
            <p className="text-sm">Start a conversation to manage your tasks</p>
            <p className="text-xs mt-1">Try: &quot;Add task: Buy groceries&quot;</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                <p
                  className={`text-xs mt-1 ${
                    message.role === 'user' ? 'text-blue-100' : 'text-gray-400'
                  }`}
                >
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message..."
            className="flex-1 resize-none border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className={`px-4 py-2 rounded-lg text-white text-sm font-medium transition-colors ${
              !input.trim() || isLoading
                ? 'bg-gray-300 cursor-not-allowed'
                : 'bg-blue-500 hover:bg-blue-600'
            }`}
          >
            Send
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-2">
          Tips: &quot;Add task: [title]&quot;, &quot;Show my tasks&quot;, &quot;Complete task [id]&quot;
        </p>
      </div>
    </div>
  );
}
