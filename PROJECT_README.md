# ChatRoom - Complete Full-Stack Application

A modern, production-ready chat application with room-based communication, direct messaging, and real-time updates. Built with Django REST Framework backend and a native HTML5/CSS3/ES6+ JavaScript frontend.

## 🚀 Features

### Backend (Django)
- ✅ User authentication with JWT tokens
- ✅ Email verification system
- ✅ Password reset functionality
- ✅ Room management (create, join, leave, delete)
- ✅ Direct messaging between users
- ✅ Group messaging in rooms
- ✅ Message reactions and threads
- ✅ Search functionality for users and rooms
- ✅ Rate limiting and security hardening
- ✅ CORS configuration
- ✅ Docker support for deployment

### Frontend (Native JS)
- ✅ Modern, responsive UI design
- ✅ Authentication flow (login, register, password reset)
- ✅ Room browsing and creation
- ✅ Real-time messaging with polling
- ✅ Direct messages
- ✅ Search functionality
- ✅ Toast notifications
- ✅ Mobile-responsive design
- ✅ Loading states and error handling
- ✅ Docker support with nginx

## 📁 Project Structure

```
/workspace/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── db.sqlite3               # SQLite database
├── media/                   # User-uploaded files
├── static/                  # Static files
├── users/                   # Users app
│   ├── models.py           # User and Profile models
│   ├── views.py            # Authentication views
│   ├── serializers.py      # User serializers
│   └── admin.py            # Admin configuration
├── rooms/                   # Rooms app
│   ├── models.py           # Room, Message, Tag models
│   ├── views.py            # Room and message views
│   ├── serializers.py      # Room serializers
│   └── admin.py            # Admin configuration
├── chat/                    # Chat app
│   ├── models.py           # Message reaction models
│   ├── serializers.py      # Chat serializers
│   └── consumers.py        # WebSocket consumers
├── core/                    # Core settings
│   └── settings.py         # Django settings
├── frontend/                # Frontend application
│   ├── index.html          # Main HTML file
│   ├── css/
│   │   └── styles.css      # All styles
│   ├── js/
│   │   ├── api.js          # API service layer
│   │   ├── auth.js         # Authentication module
│   │   ├── app.js          # Main application
│   │   ├── rooms.js        # Rooms management
│   │   ├── messages.js     # Messaging system
│   │   └── users.js        # Users management
│   ├── Dockerfile          # Frontend Docker build
│   ├── nginx.conf          # Nginx configuration
│   ├── docker-compose.yml  # Docker Compose setup
│   └── run-frontend.sh     # Development server script
├── scripts/                 # Utility scripts
│   ├── run-dev.sh          # Run development server
│   ├── run-prod.sh         # Run production server
│   ├── docker-dev.sh       # Docker development
│   ├── docker-prod.sh      # Docker production
│   ├── monitor.sh          # Server monitoring
│   └── backup.sh           # Backup utility
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── Dockerfile              # Backend Docker build
├── docker-compose.yml      # Production Docker Compose
└── docker-compose.dev.yml  # Development Docker Compose
```

## 🛠️ Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+ (optional, for frontend tooling)
- Docker & Docker Compose (optional)

### Option 1: Local Development

1. **Clone and Setup**
```bash
cd /workspace
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Run Migrations**
```bash
python manage.py migrate
```

3. **Create Superuser**
```bash
python manage.py createsuperuser
```

4. **Start Backend Server**
```bash
python manage.py runserver
```

5. **Start Frontend**
```bash
cd frontend
./run-frontend.sh
```

Visit `http://localhost:3000` to access the frontend.

### Option 2: Using Scripts

```bash
# Development mode
./scripts/run-dev.sh

# Production mode
./scripts/run-prod.sh
```

### Option 3: Docker Deployment

```bash
# Development
docker-compose -f docker-compose.dev.yml up --build

# Production
docker-compose up --build
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Rate Limiting
RATE_LIMIT_PER_HOUR=100
```

## 📡 API Endpoints

### Authentication
- `POST /api/register/` - Register new user
- `POST /api/login/` - User login
- `POST /api/logout/` - User logout
- `GET /api/user/` - Get current user
- `POST /api/token/refresh/` - Refresh access token
- `POST /api/password-reset/` - Request password reset
- `POST /api/password-reset/confirm/` - Confirm password reset
- `POST /api/verify-email/` - Verify email address
- `POST /api/resend-verification/` - Resend verification email

### Rooms
- `GET /api/rooms/` - List all rooms
- `POST /api/rooms/` - Create new room
- `GET /api/rooms/{id}/` - Get room details
- `PUT/PATCH /api/rooms/{id}/` - Update room
- `DELETE /api/rooms/{id}/` - Delete room
- `POST /api/rooms/{id}/join/` - Join room
- `POST /api/rooms/{id}/leave/` - Leave room
- `GET /api/rooms/search/` - Search rooms

### Messages
- `GET /api/messages/conversations/` - Get conversations
- `GET /api/rooms/{id}/messages/` - Get room messages
- `POST /api/rooms/{id}/messages/` - Send room message
- `GET /api/messages/{user_id}/` - Get direct messages
- `POST /api/messages/{user_id}/` - Send direct message
- `POST /api/messages/{id}/react/` - React to message
- `POST /api/messages/{id}/thread/` - Reply to thread

### Users
- `GET /api/users/` - List all users
- `GET /api/users/{id}/` - Get user details
- `GET /api/users/search/` - Search users

## 🎨 Frontend Features

### Design System
- CSS custom properties (variables)
- Consistent color palette
- Responsive breakpoints
- Modern animations and transitions

### Components
- Authentication forms
- Room cards
- Message bubbles
- User cards
- Modal dialogs
- Toast notifications
- Loading states

### Architecture
- Modular JavaScript (ES6+ classes)
- API service layer
- State management
- Event-driven architecture

## 🚢 Deployment

### Production Checklist

1. **Security**
   - [ ] Set `DEBUG=False`
   - [ ] Configure `SECRET_KEY`
   - [ ] Set up HTTPS/SSL
   - [ ] Configure allowed hosts
   - [ ] Enable security middleware
   - [ ] Set up rate limiting

2. **Database**
   - [ ] Use PostgreSQL instead of SQLite
   - [ ] Configure database backups
   - [ ] Set up connection pooling

3. **Static Files**
   - [ ] Collect static files
   - [ ] Configure CDN
   - [ ] Enable compression

4. **Email**
   - [ ] Configure production email backend
   - [ ] Set up email templates

5. **Monitoring**
   - [ ] Set up error tracking (Sentry)
   - [ ] Configure logging
   - [ ] Set up uptime monitoring

### Docker Production

```bash
# Build and start production containers
docker-compose -f docker-compose.yml up -d --build

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

## 📊 Monitoring

Use the monitoring script:

```bash
./scripts/monitor.sh
```

This provides:
- Server status
- Database health
- Active connections
- Memory usage
- Disk space

## 🧪 Testing

```bash
# Run tests
python manage.py test

# With coverage
coverage run manage.py test
coverage report
```

## 📝 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## 🙏 Acknowledgments

- Design inspired by Dribbble and Behance
- Built with Django REST Framework
- Frontend uses native web technologies
- Icons by Font Awesome

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check documentation
- Review API endpoints

---

**Built with ❤️ using Django and Modern Web Technologies**
