# Codensest

A modern, production-ready Django REST API application with real-time chat capabilities, user authentication, and room management.

## Features

- 🔐 **User Authentication**: JWT-based authentication with email verification
- 💬 **Real-time Chat**: WebSocket-powered messaging with reactions and threads
- 🏠 **Room Management**: Create, join, and manage rooms with memberships
- 🔍 **Search**: Full-text search for users and rooms
- 📧 **Email System**: Verification, password reset, and notifications
- 🚀 **Production Ready**: Docker support, monitoring, and security hardening

## Quick Start

### Local Development (Without Docker)

```bash
# Clone the repository
git clone <repository-url>
cd codensest

# Run the development server
./scripts/run-dev.sh
```

Visit http://localhost:8000 to access the API.

### Docker Development

```bash
# Start development environment
./scripts/docker-dev.sh

# View logs
./scripts/docker-dev.sh logs

# Stop environment
./scripts/docker-dev.sh stop
```

### Docker Production

```bash
# Configure environment
cp .env.example .env
# Edit .env with your production settings

# Start production environment
./scripts/docker-prod.sh

# Monitor server
./scripts/monitor.sh all
```

## Project Structure

```
codensest/
├── codensest/          # Main Django project
├── users/              # User authentication & profiles
├── rooms/              # Room management
├── chat/               # Real-time messaging
├── scripts/            # Utility scripts
│   ├── run-dev.sh      # Development server runner
│   ├── run-prod.sh     # Production server runner
│   ├── docker-dev.sh   # Docker development
│   ├── docker-prod.sh  # Docker production
│   └── monitor.sh      # Server monitoring
├── nginx/              # Nginx configuration
├── ssl/                # SSL certificates
├── Dockerfile          # Production Docker image
├── Dockerfile.dev      # Development Docker image
├── docker-compose.yml  # Production compose
├── docker-compose.dev.yml  # Development compose
└── requirements.txt    # Python dependencies
```

## API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## Available Endpoints

### Authentication
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/logout/` - User logout
- `POST /api/v1/auth/token/refresh/` - Refresh token
- `POST /api/v1/auth/verify-email/` - Verify email
- `POST /api/v1/auth/password/reset/` - Password reset

### Users
- `GET /api/v1/users/` - List users
- `GET /api/v1/users/{id}/` - User details
- `PUT /api/v1/users/{id}/` - Update user
- `GET /api/v1/users/me/` - Current user

### Rooms
- `GET /api/v1/rooms/` - List rooms
- `POST /api/v1/rooms/` - Create room
- `GET /api/v1/rooms/{id}/` - Room details
- `PUT /api/v1/rooms/{id}/` - Update room
- `DELETE /api/v1/rooms/{id}/` - Delete room

### Chat
- `GET /api/v1/messages/` - List messages
- `POST /api/v1/messages/` - Send message
- `WS /ws/chat/` - WebSocket endpoint

## Monitoring

Use the monitoring script to check server status:

```bash
# Show all information
./scripts/monitor.sh all

# Check health
./scripts/monitor.sh health

# View logs
./scripts/monitor.sh logs

# Check database
./scripts/monitor.sh db

# Docker status
./scripts/monitor.sh docker
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Essential settings
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com

# Database
DATABASE_URL=postgres://user:password@host:5432/dbname

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
```

## Security Features

- ✅ HTTPS enforcement (production)
- ✅ CORS configuration
- ✅ Rate limiting
- ✅ JWT token blacklisting
- ✅ SQL injection protection
- ✅ XSS prevention headers
- ✅ CSRF protection
- ✅ Secure password hashing

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest users/tests.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
