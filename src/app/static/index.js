let socket = io();
let currentRoom = 'General';
let username = document.getElementById('username').textContent;
let roomMessages = {};

// Socket event listeners
socket.on('connect', () => {
  highlightActiveRoom('General')
  joinRoom('General');
});

socket.on('message', (data) => {
  addMessage(
    data.username,
    data.text,
    data.username === username ? 'own' : 'other'
  );
});

socket.on('private_message', (data) => {
  addMessage(data.sender, `[Private] ${data.text}`, 'private');
});

socket.on('status', message => {
  addMessage('System', message.text, 'system');
});

socket.on('chat_history', ({ current_user, messages }) => {
  messages.forEach(message => {
    const messageType = current_user === message.username ? "own" : "other"
    addMessage(message.username, message.text, messageType);
  });
});

socket.on('online_users', (data) => {
  const userList = document.getElementById('online-users');
  userList.innerHTML = data.users
    .map(
      (user) => `
            <div class="user-item" onclick="insertPrivateMessage('${user}')">
                ${user} ${user === username ? '(you)' : ''}
            </div>
        `
    )
    .join('');
});

// Message handling
function addMessage(sender, message, type) {
  if (!roomMessages[currentRoom]) {
    roomMessages[currentRoom] = [];
  }
  // if (type !== "system") {
  //   roomMessages[currentRoom].push({ sender, message, type });
  // }
  const chat = document.getElementById('chat');
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${type}`;
  messageDiv.textContent = `${sender}: ${message}`;
  chat.appendChild(messageDiv);
  chat.scrollTop = chat.scrollHeight;
}

function sendMessage() {
  const input = document.getElementById('message');
  const message = input.value.trim();

  if (!message) return;

  if (message.startsWith('@')) {
    // Send private message
    const [receiver, ...msgParts] = message.substring(1).split(' ');
    const privateMsg = msgParts.join(' ');

    if (privateMsg) {
      socket.emit('message', { text: privateMsg, type: 'private', receiver: receiver });
    }
  } else {
    // Send room message
    socket.emit('message', { text: message, room: currentRoom });
  }

  input.value = '';
  input.focus();
}

function joinRoom(room) {
  if (room === currentRoom) return false;
  socket.emit('leave', { room: currentRoom });
  currentRoom = room;
  socket.emit('join', { room });

  highlightActiveRoom(room);

  // Show room history
  const chat = document.getElementById('chat');
  chat.innerHTML = '';

  if (roomMessages[room]) {
    roomMessages[room].forEach((msg) => {
      addMessage(msg.sender, msg.message, msg.type);
    });
  }
}

function insertPrivateMessage(user) {
  document.getElementById('message').value = `@${user} `;
  document.getElementById('message').focus();
}

function handleKeyPress(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}

// Initialize chat when page loads
let chat;
document.addEventListener('DOMContentLoaded', () => {
  chat = new ChatApp();
  if ('Notification' in window) {
    Notification.requestPermission();
  }
});

// Add this new function to handle room highlighting
function highlightActiveRoom(room) {
  document.querySelectorAll('.room-item').forEach((item) => {
    item.classList.remove('active-room');
    if (item.textContent.trim() === room) {
      item.classList.add('active-room');
    }
  });
}
