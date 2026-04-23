# ChatRoom - Frontend

A modern, responsive web application for real-time chat and room-based communication. Built with native HTML5, CSS3, and ES6+ JavaScript.

## Features

- **Authentication**: Login, registration, password reset
- **Rooms**: Create, join, and manage chat rooms
- **Messaging**: Real-time direct messages and room chats
- **Search**: Find users and rooms quickly
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern UI**: Clean design inspired by Dribbble and Behance trends

## Quick Start

### Option 1: Direct File Access
Simply open `index.html` in your browser:

```bash
# Using Python's built-in server
cd frontend
python -m http.server 3000

# Or using Node.js
npx serve .
```

### Option 2: Using the Run Script
```bash
./run-frontend.sh
```

## Project Structure

```
frontend/
├── index.html          # Main HTML file
├── css/
│   └── styles.css      # All styles (CSS variables, components, responsive)
├── js/
│   ├── api.js          # API service layer
│   ├── auth.js         # Authentication module
│   ├── app.js          # Main application controller
│   ├── rooms.js        # Rooms management
│   ├── messages.js     # Messaging system
│   └── users.js        # Users management
└── images/             # Static images (if needed)
```

## Configuration

Edit the API configuration in `js/api.js`:

```javascript
const API_CONFIG = {
    baseURL: 'http://localhost:8000/api',  // Change to your backend URL
    timeout: 10000,
};
```

## Key Features

### Authentication
- Secure login with JWT tokens
- User registration with email verification
- Password reset functionality
- Automatic token refresh

### Rooms
- Create public or private rooms
- Add tags for organization
- View member count
- Join/leave rooms

### Messaging
- Real-time message polling
- Direct messages between users
- Room-based group chats
- Message history
- Unread message indicators

### User Experience
- Toast notifications
- Loading states
- Error handling
- Responsive mobile menu
- Smooth animations

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development

### Adding New Features

1. **New Module**: Create a new JS file in the `js/` directory
2. **Styles**: Add component styles to `css/styles.css`
3. **HTML**: Update `index.html` if new views are needed

### Code Style

- ES6+ JavaScript with classes
- CSS custom properties (variables)
- BEM-like naming convention
- Modular architecture

## Deployment

### Production Build

For production, consider:

1. Minify CSS and JavaScript
2. Enable gzip compression
3. Set up a CDN for static assets
4. Configure proper CORS headers on the backend

### Docker Deployment

```bash
# Build and run with Docker
docker-compose -f docker-compose.dev.yml up frontend
```

## API Integration

The frontend expects the following API endpoints:

### Authentication
- `POST /api/login/` - User login
- `POST /api/register/` - User registration
- `POST /api/logout/` - User logout
- `GET /api/user/` - Get current user
- `POST /api/token/refresh/` - Refresh token
- `POST /api/password-reset/` - Request password reset

### Rooms
- `GET /api/rooms/` - List rooms
- `POST /api/rooms/` - Create room
- `GET /api/rooms/{id}/` - Get room details
- `POST /api/rooms/{id}/join/` - Join room
- `POST /api/rooms/{id}/leave/` - Leave room
- `DELETE /api/rooms/{id}/` - Delete room
- `GET /api/rooms/search/` - Search rooms

### Messages
- `GET /api/messages/conversations/` - Get conversations
- `GET /api/rooms/{id}/messages/` - Get room messages
- `POST /api/rooms/{id}/messages/` - Send room message
- `GET /api/messages/{user_id}/` - Get direct messages
- `POST /api/messages/{user_id}/` - Send direct message

### Users
- `GET /api/users/` - List users
- `GET /api/users/{id}/` - Get user details
- `GET /api/users/search/` - Search users

## Troubleshooting

### Common Issues

**CORS Errors**: Ensure your backend has proper CORS configuration.

**Authentication Failures**: Check that tokens are being stored correctly in localStorage.

**API Connection**: Verify the `baseURL` in `js/api.js` matches your backend.

## License

MIT License

## Credits

Design inspired by modern UI/UX trends from Dribbble and Behance.
