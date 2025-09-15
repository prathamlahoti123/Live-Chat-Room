let socket = io();

let currentRoom = '';
let currentUser = document.getElementById('username').textContent;

socket.on('connect', () => {
  highlightActiveRoom(currentRoom)
  joinRoom(currentRoom);
});

socket.on('message', message => {
  addMessage(
    message.username,
    message.text,
    message.timestamp,
    message.username === currentUser ? 'own' : 'other'
  );
});

socket.on('private_message', message => {
  addMessage(message.sender, `[Private] ${message.text}`, message.timestamp, 'private');
});

socket.on('status', message => {
  addSystemMessage(message.text);
});

socket.on('chat_history', ({ messages }) => {
  messages.forEach(message => {
    addMessage(
      message.username,
      message.text,
      message.timestamp,
      currentUser === message.username ? "own" : "other"
    );
  });
});

socket.on('online_users', data => {
  const userList = document.getElementById('online-users');
  userList.innerHTML = data.users
    .map(
      user => `
        <div class="user-item" onclick="insertPrivateMessage('${user}')">
          ${user} ${user === currentUser ? '(you)' : ''}
        </div>
      `
    )
    .join('');
});


function addSystemMessage(message) {
  const chat = document.getElementById('chat');
  const messageDiv = document.createElement('div');
  messageDiv.className = `message system`;
  messageDiv.textContent = `System: ${message}`;
  chat.appendChild(messageDiv);
}


// Message handling
function addMessage(sender, message, timestamp, type) {
  const chat = document.getElementById('chat');
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${type}`;

  const messageAuthor = document.createElement('span');
  messageAuthor.className = 'message-author';
  messageAuthor.textContent = `${sender}: `;
  messageAuthor.onclick = () => insertPrivateMessage(sender);
  messageDiv.appendChild(messageAuthor);

  const messageText = document.createElement('span');
  messageText.className = 'message-text';
  messageText.textContent = message;
  messageDiv.appendChild(messageText);

  const messageTimestamp = document.createElement('span');
  messageTimestamp.className = 'message-timestamp';
  messageTimestamp.textContent = formatTimestamp(timestamp);
  messageDiv.appendChild(messageTimestamp);

  chat.appendChild(messageDiv);
  chat.scrollTop = chat.scrollHeight;
}

function sendPrivateMessage(message) {
  const [receiver, ...textParts] = message.substring(1).split(' ');
  const text = textParts.join(' ');
  if (text) {
    socket.emit('message', { text, receiver, type: 'private' });
  }
}

function sendPublicMessage(message, room) {
  socket.emit('message', { text: message, room });
}

function sendMessage() {
  const input = document.getElementById('message');
  const message = input.value.trim();
  if (!message) return;
  message.startsWith('@')
    ? sendPrivateMessage(message)
    : sendPublicMessage(message, currentRoom);
  input.value = '';
  input.focus();
}

function joinRoom(room) {
  if (room === currentRoom) return;
  socket.emit('leave', { room: currentRoom });
  currentRoom = room;
  socket.emit('join', { room });

  highlightActiveRoom(room);

  // Clear chat window
  const chat = document.getElementById('chat');
  chat.innerHTML = '';
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

function formatTimestamp(timestamp) {
  // convert Unix timestamp to milliseconds
  const date = new Date(timestamp * 1000);
  return date.toLocaleString("en-US", {
    month: "long",
    day: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
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
