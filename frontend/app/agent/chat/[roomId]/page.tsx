'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSocket } from '@/hooks/useSocket';
import { useChat } from '@/hooks/useChat';
import {
  MessageBubble,
  TypingIndicator,
  ConnectionStatus,
  EmptyState,
} from '@/components/chat';

export default function AgentChatPage({ params }: { params: { roomId: string } }) {
  const router = useRouter();
  const { socket, isConnected } = useSocket();
  const [inputText, setInputText] = useState('');
  const [showTranslation, setShowTranslation] = useState(true);
  const [agentId, setAgentId] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const savedAgentId = localStorage.getItem('agent_id') || `agent_${Date.now()}`;
    setAgentId(savedAgentId);
  }, []);

  const {
    messages,
    isTyping,
    isOnline,
    sendMessage,
    sendTyping,
    sendStopTyping,
  } = useChat({
    socket,
    roomId: params.roomId,
    userType: 'agent',
    language: 'ko',
    agentId,
  });

  // Auto scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!inputText.trim() || !isConnected) return;
    sendMessage(inputText);
    setInputText('');
    sendStopTyping();
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputText(e.target.value);
    sendTyping();
  };

  const handleEndChat = () => {
    if (confirm('Are you sure you want to end this chat?')) {
      router.push('/agent');
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-lg">
        <div className="px-4 py-4 sm:px-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={() => router.push('/agent')}
                className="p-2 hover:bg-white/20 rounded-lg transition-all"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <div className="relative">
                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" />
                  </svg>
                </div>
                <div className={`absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full border-2 border-purple-600 ${
                  isOnline ? 'bg-green-400' : 'bg-gray-400'
                }`} />
              </div>
              <div>
                <h1 className="text-lg font-semibold">Customer Chat</h1>
                <p className="text-xs text-purple-100">
                  {isOnline ? 'Customer is online' : 'Waiting for customer'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowTranslation(!showTranslation)}
                className="px-3 py-1.5 bg-white/20 hover:bg-white/30 rounded-lg text-xs font-medium transition-all"
              >
                {showTranslation ? 'Hide' : 'Show'} Translation
              </button>
              <button
                onClick={handleEndChat}
                className="px-3 py-1.5 bg-red-500/80 hover:bg-red-500 rounded-lg text-xs font-medium transition-all"
              >
                End Chat
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Connection Status */}
      <ConnectionStatus isConnected={isConnected} />

      {/* Room Info */}
      <div className="px-4 py-2 bg-white border-b border-gray-200 text-sm text-gray-600">
        <span className="font-medium">Room ID:</span> {params.roomId}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.length === 0 ? (
          <EmptyState />
        ) : (
          <>
            {messages.map((msg) => (
              <MessageBubble
                key={msg.id}
                message={msg}
                showTranslation={showTranslation}
              />
            ))}
            {isTyping && <TypingIndicator />}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="px-4 py-4 bg-white border-t border-gray-200 shadow-lg">
        <div className="flex gap-2 items-end">
          <div className="flex-1">
            <input
              ref={inputRef}
              type="text"
              value={inputText}
              onChange={handleInputChange}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
              placeholder={
                isConnected
                  ? 'Type your message in Korean...'
                  : 'Connecting...'
              }
              disabled={!isConnected}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl
                focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent
                disabled:bg-gray-100 disabled:cursor-not-allowed
                text-sm sm:text-base
                transition-all duration-200"
            />
          </div>
          <button
            onClick={handleSend}
            disabled={!inputText.trim() || !isConnected}
            className="px-5 py-3 bg-purple-600 text-white rounded-xl
              hover:bg-purple-700 active:bg-purple-800
              disabled:bg-gray-300 disabled:cursor-not-allowed
              transition-all duration-200
              flex items-center justify-center gap-2
              font-medium text-sm sm:text-base
              shadow-md hover:shadow-lg
              min-w-[80px]"
            aria-label="Send message"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
            <span className="hidden sm:inline">Send</span>
          </button>
        </div>
      </div>
    </div>
  );
}
