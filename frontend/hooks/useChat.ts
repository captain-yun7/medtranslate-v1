import { useState, useEffect, useCallback } from 'react';
import { Socket } from 'socket.io-client';
import { Message } from '@/types';

interface UseChatProps {
  socket: Socket | null;
  roomId: string;
  userType: 'customer' | 'agent';
  language?: string;
}

export function useChat({ socket, roomId, userType, language }: UseChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [isOnline, setIsOnline] = useState(false);

  useEffect(() => {
    if (!socket) return;

    // 방 입장
    socket.emit('join_room', {
      room_id: roomId,
      user_type: userType,
      customer_language: language,
    });

    // 입장 확인
    socket.on('joined_room', (data) => {
      console.log('Joined room:', data);
    });

    // 메시지 수신
    if (userType === 'customer') {
      socket.on('customer_receive_message', (data) => {
        setMessages(prev => [...prev, {
          id: data.message_id,
          type: 'received',
          text: data.message,
          timestamp: data.timestamp,
        }]);
      });

      socket.on('message_sent', (data) => {
        setMessages(prev => [...prev, {
          id: data.message_id,
          type: 'sent',
          text: data.message,
          timestamp: data.timestamp,
        }]);
      });

      socket.on('agent_online', () => {
        setIsOnline(true);
      });
    } else {
      // agent
      socket.on('agent_receive_message', (data) => {
        setMessages(prev => [...prev, {
          id: data.message_id,
          type: 'received',
          original: data.original,
          translated: data.translated,
          text: data.translated,
          sourceLang: data.source_lang,
          timestamp: data.timestamp,
        }]);
      });

      socket.on('message_sent', (data) => {
        setMessages(prev => [...prev, {
          id: data.message_id,
          type: 'sent',
          text: data.original,
          translated: data.translated,
          timestamp: data.timestamp,
        }]);
      });

      socket.on('customer_online', (data) => {
        setIsOnline(true);
      });
    }

    // 타이핑 표시
    socket.on('user_typing', () => {
      setIsTyping(true);
    });

    socket.on('user_stop_typing', () => {
      setIsTyping(false);
    });

    // 채팅 종료
    socket.on('chat_ended', () => {
      console.log('Chat ended');
    });

    return () => {
      socket.off('joined_room');
      socket.off('customer_receive_message');
      socket.off('agent_receive_message');
      socket.off('message_sent');
      socket.off('user_typing');
      socket.off('user_stop_typing');
      socket.off('chat_ended');
    };
  }, [socket, roomId, userType, language]);

  const sendMessage = useCallback((message: string) => {
    if (!socket || !message.trim()) return;

    const event = userType === 'customer' ? 'customer_message' : 'agent_message';

    socket.emit(event, {
      room_id: roomId,
      message: message,
      timestamp: new Date().toISOString(),
    });
  }, [socket, roomId, userType]);

  const sendTyping = useCallback(() => {
    if (!socket) return;
    socket.emit('typing', {
      room_id: roomId,
      user_type: userType,
    });
  }, [socket, roomId, userType]);

  const sendStopTyping = useCallback(() => {
    if (!socket) return;
    socket.emit('stop_typing', {
      room_id: roomId,
      user_type: userType,
    });
  }, [socket, roomId, userType]);

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
