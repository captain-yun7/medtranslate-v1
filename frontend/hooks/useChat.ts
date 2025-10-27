import { useState, useEffect, useCallback } from 'react';
import { Socket } from 'socket.io-client';
import { Message } from '@/types';

interface UseChatProps {
  socket: Socket | null;
  roomId: string;
  userType: 'customer' | 'agent';
  language?: string;
  agentId?: string;
}

export function useChat({ socket, roomId, userType, language, agentId }: UseChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [isOnline, setIsOnline] = useState(false);

  useEffect(() => {
    if (!socket) return;

    // 방 입장
    socket.emit('join_room', {
      room_id: roomId,
      user_type: userType,
      language: language,
      agent_id: agentId,
    });

    // 입장 확인
    socket.on('joined_room', (data) => {
      console.log('Joined room:', data);
    });

    // 통합 메시지 수신
    socket.on('new_message', (data) => {
      const messageType = data.sender_type === userType ? 'sent' : 'received';

      setMessages(prev => [...prev, {
        id: `msg_${Date.now()}_${Math.random()}`,
        type: messageType,
        text: data.text,
        translated: data.translated_text,
        sourceLang: data.source_lang,
        targetLang: data.target_lang,
        timestamp: new Date().toISOString(),
      }]);
    });

    // 온라인 상태
    if (userType === 'customer') {
      socket.on('agent_online', () => {
        setIsOnline(true);
      });
    } else {
      socket.on('customer_online', (data) => {
        setIsOnline(true);
      });
    }

    // 타이핑 표시
    socket.on('typing', () => {
      setIsTyping(true);
    });

    socket.on('stop_typing', () => {
      setIsTyping(false);
    });

    // 채팅 종료
    socket.on('chat_ended', () => {
      console.log('Chat ended');
    });

    return () => {
      socket.off('joined_room');
      socket.off('new_message');
      socket.off('agent_online');
      socket.off('customer_online');
      socket.off('typing');
      socket.off('stop_typing');
      socket.off('chat_ended');
    };
  }, [socket, roomId, userType, language, agentId]);

  const sendMessage = useCallback((message: string) => {
    if (!socket || !message.trim()) return;

    socket.emit('send_message', {
      room_id: roomId,
      text: message,
      language: language || 'ko',
    });
  }, [socket, roomId, language]);

  const sendTyping = useCallback(() => {
    if (!socket) return;
    socket.emit('typing', {
      room_id: roomId,
    });
  }, [socket, roomId]);

  const sendStopTyping = useCallback(() => {
    if (!socket) return;
    socket.emit('stop_typing', {
      room_id: roomId,
    });
  }, [socket, roomId]);

  const endChat = useCallback(() => {
    if (!socket) return;
    socket.emit('end_chat', {
      room_id: roomId,
      ended_by: userType,
    });
  }, [socket, roomId, userType]);

  return {
    messages,
    isTyping,
    isOnline,
    sendMessage,
    sendTyping,
    sendStopTyping,
    endChat,
  };
}
