const io = require('socket.io-client');

// Test configuration
const BACKEND_URL = 'http://localhost:8001';
const TEST_ROOM_ID = 'room_b08d74518b35';

console.log('Starting end-to-end chat test...\n');

// Customer socket
const customerSocket = io(BACKEND_URL, {
  transports: ['websocket'],
  reconnection: false,
  extraHeaders: { 'Origin': 'http://localhost:3001' }
});

// Agent socket
const agentSocket = io(BACKEND_URL, {
  transports: ['websocket'],
  reconnection: false,
  extraHeaders: { 'Origin': 'http://localhost:3002' }
});

let customerConnected = false;
let agentConnected = false;
let testsPassed = 0;
let testsFailed = 0;

// Customer connection
customerSocket.on('connect', () => {
  console.log('✅ Customer connected:', customerSocket.id);
  customerConnected = true;
  testsPassed++;

  // Join room as customer
  customerSocket.emit('join_room', {
    room_id: TEST_ROOM_ID,
    user_type: 'customer',
    language: 'vi'
  });
});

customerSocket.on('joined_room', (data) => {
  console.log('✅ Customer joined room:', data);
  testsPassed++;

  // Send a test message
  setTimeout(() => {
    console.log('\n📤 Customer sending message: "Hello, I need help"');
    customerSocket.emit('send_message', {
      room_id: TEST_ROOM_ID,
      text: 'Hello, I need help',
      language: 'en'
    });
  }, 500);
});

customerSocket.on('new_message', (data) => {
  console.log('✅ Customer received message:', {
    from: data.sender_type,
    original: data.text,
    translated: data.translated_text
  });
  testsPassed++;
});

customerSocket.on('typing', (data) => {
  console.log('⌨️  Agent is typing...');
});

customerSocket.on('stop_typing', () => {
  console.log('⌨️  Agent stopped typing');
});

// Agent connection
agentSocket.on('connect', () => {
  console.log('✅ Agent connected:', agentSocket.id);
  agentConnected = true;
  testsPassed++;

  // Join room as agent
  agentSocket.emit('join_room', {
    room_id: TEST_ROOM_ID,
    user_type: 'agent',
    agent_id: 'agent_test_001'
  });
});

agentSocket.on('joined_room', (data) => {
  console.log('✅ Agent joined room:', data);
  testsPassed++;

  // Wait for customer message, then reply
  setTimeout(() => {
    console.log('\n⌨️  Agent starts typing...');
    agentSocket.emit('typing', { room_id: TEST_ROOM_ID });

    setTimeout(() => {
      console.log('📤 Agent sending message: "안녕하세요, 어떻게 도와드릴까요?"');
      agentSocket.emit('send_message', {
        room_id: TEST_ROOM_ID,
        text: '안녕하세요, 어떻게 도와드릴까요?',
        language: 'ko'
      });

      agentSocket.emit('stop_typing', { room_id: TEST_ROOM_ID });
    }, 1000);
  }, 2000);
});

agentSocket.on('new_message', (data) => {
  console.log('✅ Agent received message:', {
    from: data.sender_type,
    original: data.text,
    translated: data.translated_text
  });
  testsPassed++;
});

// Error handlers
customerSocket.on('connect_error', (error) => {
  console.error('❌ Customer connection failed:', error.message);
  testsFailed++;
});

customerSocket.on('error', (error) => {
  console.error('❌ Customer error:', error);
  testsFailed++;
});

agentSocket.on('connect_error', (error) => {
  console.error('❌ Agent connection failed:', error.message);
  testsFailed++;
});

agentSocket.on('error', (error) => {
  console.error('❌ Agent error:', error);
  testsFailed++;
});

// Test completion
setTimeout(() => {
  console.log('\n' + '='.repeat(50));
  console.log('Test Results:');
  console.log('='.repeat(50));
  console.log(`✅ Tests passed: ${testsPassed}`);
  console.log(`❌ Tests failed: ${testsFailed}`);
  console.log('='.repeat(50));

  customerSocket.disconnect();
  agentSocket.disconnect();

  process.exit(testsFailed > 0 ? 1 : 0);
}, 5000);
