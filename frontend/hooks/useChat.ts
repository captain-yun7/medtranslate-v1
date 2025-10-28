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

      // Agent의 경우 received 메시지는 한국어 번역을 주 텍스트로 표시
      // Customer의 경우 received 메시지는 번역된 외국어를 주 텍스트로 표시
      let displayText = data.text;
      let displayTranslated = data.translated_text;

      if (userType === 'agent' && messageType === 'received') {
        // 상담사가 고객 메시지를 받을 때: 한국어 번역을 주로, 원문을 번역으로
        displayText = data.translated_text;
        displayTranslated = data.text;
      } else if (userType === 'agent' && messageType === 'sent') {
        // 상담사가 보낸 메시지: 한국어만 표시 (번역 없음)
        displayText = data.text;
        displayTranslated = undefined;
      } else if (userType === 'customer' && messageType === 'received') {
        // 고객이 상담사 메시지를 받을 때: 번역된 외국어를 주로, 한국어 원문을 번역으로
        displayText = data.text;
        displayTranslated = data.translated_text;
      } else if (userType === 'customer' && messageType === 'sent') {
        // 고객이 보낸 메시지: 외국어만 표시 (번역 없음)
        displayText = data.text;
        displayTranslated = undefined;
      }

      setMessages(prev => [...prev, {
        id: `msg_${Date.now()}_${Math.random()}`,
        type: messageType,
        text: displayText,
        translated: displayTranslated,
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
