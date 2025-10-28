'use client';

import { useState, useRef, useEffect } from 'react';
import { useSocket } from '@/hooks/useSocket';
import { useChat } from '@/hooks/useChat';
import {
  MessageBubble,
  TypingIndicator,
  ConnectionStatus,
  EmptyState,
  LanguageSelector,
} from '@/components/chat';

export default function ChatPage({ params }: { params: { roomId: string } }) {
  const { socket, isConnected, isReconnecting } = useSocket();
  const [inputText, setInputText] = useState('');
  const [language, setLanguage] = useState('vi');
  const [showTranslation, setShowTranslation] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

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
    userType: 'customer',
    language,
  });

  // 자동 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!inputText.trim() || !isConnected) return;
    sendMessage(inputText);
    setInputText('');
    sendStopTyping();
    // 전송 후 입력창에 포커스
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputText(e.target.value);
    sendTyping();
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      {/* 헤더 */}
      <header className="bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg">
        <div className="px-4 py-4 sm:px-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {/* 상담사 온라인 상태 */}
              <div className="relative">
                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" />
                  </svg>
                </div>
                <div className={`absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full border-2 border-blue-600 ${
                  isOnline ? 'bg-green-400' : 'bg-gray-400'
                }`} />
              </div>
              <div>
                <h1 className="text-lg font-semibold">의료 상담</h1>
                <p className="text-xs text-blue-100">
                  {isOnline ? '상담사가 대기 중입니다' : '상담사 연결 대기 중'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* 연결 상태 알림 */}
      <ConnectionStatus isConnected={isConnected} isReconnecting={isReconnecting} />

      {/* 언어 선택 */}
      <div className="px-4 py-3 bg-white border-b border-gray-200 shadow-sm">
        <LanguageSelector
          value={language}
          onChange={setLanguage}
          disabled={!isConnected}
        />
      </div>

      {/* 메시지 영역 */}
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

      {/* 입력 영역 */}
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
                  ? '메시지를 입력하세요...'
                  : '연결 대기 중...'
              }
              disabled={!isConnected}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                disabled:bg-gray-100 disabled:cursor-not-allowed
                text-sm sm:text-base
                transition-all duration-200"
            />
          </div>
          <button
            onClick={handleSend}
            disabled={!inputText.trim() || !isConnected}
            className="px-5 py-3 bg-blue-600 text-white rounded-xl
              hover:bg-blue-700 active:bg-blue-800
              disabled:bg-gray-300 disabled:cursor-not-allowed
              transition-all duration-200
              flex items-center justify-center gap-2
              font-medium text-sm sm:text-base
              shadow-md hover:shadow-lg
              min-w-[80px]"
            aria-label="메시지 전송"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
            <span className="hidden sm:inline">전송</span>
          </button>
        </div>
      </div>
    </div>
  );
}
