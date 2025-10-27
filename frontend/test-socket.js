const io = require('socket.io-client');

const socket = io('http://localhost:8001', {
  transports: ['websocket'],
  reconnection: false,
  extraHeaders: {
    'Origin': 'http://localhost:3001'
  }
});

socket.on('connect', () => {
  console.log('✅ Socket.io connection successful!');
  console.log('Socket ID:', socket.id);

  // Test joining a room
  socket.emit('join_room', {
    room_id: 'room_b08d74518b35',
    user_type: 'customer',
    language: 'vi'
  });

  setTimeout(() => {
    socket.disconnect();
    console.log('Test completed successfully');
    process.exit(0);
  }, 2000);
});

socket.on('connect_error', (error) => {
  console.error('❌ Connection failed:', error.message);
  process.exit(1);
});

socket.on('room_joined', (data) => {
  console.log('✅ Room joined successfully:', data);
});

socket.on('error', (error) => {
  console.error('❌ Socket error:', error);
});

setTimeout(() => {
  if (!socket.connected) {
    console.error('❌ Connection timeout');
    process.exit(1);
  }
}, 5000);
