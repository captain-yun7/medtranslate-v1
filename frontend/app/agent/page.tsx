'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface ChatRoom {
  id: string;
  customer_language: string;
  agent_id: string | null;
  status: string;
  created_at: string;
}

export default function AgentConsolePage() {
  const router = useRouter();
  const [rooms, setRooms] = useState<ChatRoom[]>([]);
  const [activeRooms, setActiveRooms] = useState<ChatRoom[]>([]);
  const [agentId, setAgentId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Load agent ID and JWT token from localStorage
  useEffect(() => {
    const token = localStorage.getItem('jwt_token');
    const savedAgentId = localStorage.getItem('agent_id');

    if (token) {
      setIsAuthenticated(true);
      if (savedAgentId) {
        setAgentId(savedAgentId);
      }
    } else {
      // Fallback for old localStorage format
      const fallbackAgentId = localStorage.getItem('agent_id') || `agent_${Date.now()}`;
      setAgentId(fallbackAgentId);
      localStorage.setItem('agent_id', fallbackAgentId);
    }
  }, []);

  // Fetch waiting and active rooms
  const fetchRooms = async () => {
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('jwt_token');

      if (token && isAuthenticated) {
        // Use authenticated API for agent-specific rooms
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat/agent/rooms?include_waiting=true`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          if (response.status === 401) {
            setIsAuthenticated(false);
            throw new Error('Authentication required. Please log in.');
          }
          throw new Error('Failed to fetch rooms');
        }

        const data = await response.json();

        // Separate active and waiting rooms
        const active = data.filter((room: ChatRoom) =>
          room.agent_id && (room.status === 'active' || room.status === 'waiting')
        );
        const waiting = data.filter((room: ChatRoom) =>
          !room.agent_id && room.status === 'waiting'
        );

        setActiveRooms(active);
        setRooms(waiting);
      } else {
        // Fallback to public API
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat/rooms`);
        if (!response.ok) throw new Error('Failed to fetch rooms');
        const data = await response.json();
        setRooms(data.filter((room: ChatRoom) => room.status === 'waiting'));
        setActiveRooms([]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load rooms');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRooms();
    const interval = setInterval(fetchRooms, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [isAuthenticated]);

  const handleJoinRoom = async (roomId: string, needsAssignment: boolean = false) => {
    const token = localStorage.getItem('jwt_token');

    // If room needs assignment and user is authenticated
    if (needsAssignment && token) {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/chat/rooms/${roomId}/assign`,
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );

        if (!response.ok) {
          throw new Error('Failed to assign room');
        }

        await fetchRooms(); // Refresh room list
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to assign room');
        return;
      }
    }

    router.push(`/agent/chat/${roomId}`);
  };

  const createTestRoom = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat/rooms`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customer_language: 'vi' })
      });
      if (!response.ok) throw new Error('Failed to create room');
      await fetchRooms();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create room');
    }
  };

  const handleLogin = () => {
    router.push('/agent/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-lg">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Agent Console</h1>
              <p className="text-sm text-purple-100 mt-1">
                {isAuthenticated ? `Agent ID: ${agentId}` : 'Not authenticated'}
              </p>
            </div>
            <div className="flex gap-2">
              {!isAuthenticated && (
                <button
                  onClick={handleLogin}
                  className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg text-sm font-medium transition-all"
                >
                  Login
                </button>
              )}
              <button
                onClick={createTestRoom}
                className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg text-sm font-medium transition-all"
              >
                Create Test Room
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Active Chats Section */}
        {isAuthenticated && activeRooms.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-800 flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                My Active Chats ({activeRooms.length})
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {activeRooms.map((room) => (
                <div
                  key={room.id}
                  onClick={() => handleJoinRoom(room.id, false)}
                  className="p-4 border-2 border-purple-200 bg-purple-50 rounded-lg hover:border-purple-400 hover:shadow-md transition-all cursor-pointer"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-purple-600 uppercase">
                      {room.customer_language}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      room.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                    }`}>
                      {room.status}
                    </span>
                  </div>
                  <p className="text-sm font-mono text-gray-600 truncate mb-2">{room.id}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(room.created_at).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Waiting Rooms Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-800">
              Waiting Rooms ({rooms.length})
            </h2>
            <button
              onClick={fetchRooms}
              disabled={loading}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 transition-all text-sm font-medium"
            >
              {loading ? 'Loading...' : 'Refresh'}
            </button>
          </div>

          {rooms.length === 0 ? (
            <div className="text-center py-12">
              <svg
                className="w-16 h-16 mx-auto text-gray-300 mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
              <p className="text-gray-500 text-lg mb-2">No waiting customers</p>
              <p className="text-gray-400 text-sm">
                Rooms will appear here when customers join
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {rooms.map((room) => (
                <div
                  key={room.id}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-purple-300 hover:bg-purple-50 transition-all"
                >
                  <div>
                    <p className="font-medium text-gray-800">{room.id}</p>
                    <div className="flex items-center gap-3 mt-1 text-sm text-gray-600">
                      <span>Language: {room.customer_language.toUpperCase()}</span>
                      <span>•</span>
                      <span>{new Date(room.created_at).toLocaleTimeString()}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleJoinRoom(room.id, isAuthenticated)}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all text-sm font-medium"
                  >
                    {isAuthenticated ? 'Accept Chat' : 'Join Chat'}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div className="bg-white rounded-lg shadow-md p-4">
            <p className="text-sm text-gray-600">Active Chats</p>
            <p className="text-2xl font-bold text-purple-600">{activeRooms.length}</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-4">
            <p className="text-sm text-gray-600">Waiting Rooms</p>
            <p className="text-2xl font-bold text-orange-600">{rooms.length}</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-4">
            <p className="text-sm text-gray-600">Status</p>
            <p className="text-2xl font-bold text-green-600">
              {isAuthenticated ? 'Authenticated' : 'Guest'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
