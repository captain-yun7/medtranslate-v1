import { useEffect, useState, useRef } from 'react';
import { io, Socket } from 'socket.io-client';

const SOCKET_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function useSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [isReconnecting, setIsReconnecting] = useState(false);
  const [reconnectAttempt, setReconnectAttempt] = useState(0);
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    const socket = io(SOCKET_URL, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 10,
      timeout: 10000,
    });

    socket.on('connect', () => {
      console.log('Socket connected:', socket.id);
      setIsConnected(true);
      setIsReconnecting(false);
      setReconnectAttempt(0);
    });

    socket.on('disconnect', (reason) => {
      console.log('Socket disconnected:', reason);
      setIsConnected(false);

      // 서버 종료나 클라이언트 의도적 종료가 아니면 재연결 시도
      if (reason !== 'io server disconnect' && reason !== 'io client disconnect') {
        setIsReconnecting(true);
      }
    });

    socket.on('reconnect_attempt', (attemptNumber) => {
      console.log('Reconnection attempt:', attemptNumber);
      setReconnectAttempt(attemptNumber);
      setIsReconnecting(true);
    });

    socket.on('reconnect', (attemptNumber) => {
      console.log('Reconnected successfully after', attemptNumber, 'attempts');
      setIsConnected(true);
      setIsReconnecting(false);
      setReconnectAttempt(0);
    });

    socket.on('reconnect_error', (error) => {
      console.error('Reconnection error:', error);
    });

    socket.on('reconnect_failed', () => {
      console.error('Reconnection failed after all attempts');
      setIsReconnecting(false);
      setIsConnected(false);
    });

    socket.on('connect_error', (error) => {
      console.error('Connection error:', error);
      setIsConnected(false);
    });

    socket.on('error', (error) => {
      console.error('Socket error:', error);
    });

    socketRef.current = socket;

    return () => {
      socket.disconnect();
    };
  }, []);

  return {
    socket: socketRef.current,
    isConnected,
    isReconnecting,
    reconnectAttempt,
  };
}
