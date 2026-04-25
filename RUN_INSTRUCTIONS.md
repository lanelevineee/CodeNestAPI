# CodeNest - Running Instructions

## Quick Start

### Option 1: Manual Setup (Development)

#### 1. Backend (Django API)

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser

# Run development server
python manage.py runserver 0.0.0.0:8000
```

Backend will be available at: `http://localhost:8000`
API endpoints: `http://localhost:8000/api/v1/`
Admin dashboard: `http://localhost:8000/admin/`

#### 2. Frontend (Client Web App)

```bash
# Navigate to frontend directory
cd frontend

# Start simple HTTP server
python -m http.server 8083
```

Frontend will be available at: `http://localhost:8083`
Admin panel: `http://localhost:8083/pages/admin.html`

### Option 2: Using Shell Scripts

```bash
# Development mode
./run-dev.sh

# Production mode (requires Docker)
./run-prod.sh

# Docker development
./docker-dev.sh

# Docker production
./docker-prod.sh

# Server monitoring
./monitor.sh
```

### Option 3: Docker Compose

#### Development
```bash
docker-compose -f docker-compose.dev.yml up -d
```

#### Production
```bash
docker-compose up -d
```

## Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Backend API | http://localhost:8000 | Django REST API |
| Frontend Client | http://localhost:8083 | Main web application |
| Admin Dashboard | http://localhost:8083/pages/admin.html | Server management & monitoring |
| Django Admin | http://localhost:8000/admin/ | Django admin interface |
| API Docs | http://localhost:8000/api/docs/ | Swagger documentation |

## Default Credentials

After running `createsuperuser`:
- Email: (your email)
- Password: (your password)

## Environment Variables

Key variables in `.env`:
- `DEBUG=True` - Enable debug mode (development only)
- `SECRET_KEY=` - Your Django secret key
- `ALLOWED_HOSTS=` - Comma-separated list of allowed hosts
- `DATABASE_URL=` - PostgreSQL connection string
- `REDIS_URL=` - Redis connection string
- `CORS_ALLOW_ALL=True` - Allow all CORS origins (development)
- `EMAIL_*` - Email configuration

## Troubleshooting

### CORS Errors
Make sure CORS is properly configured in `.env`:
```
CORS_ALLOW_ALL=True
CORS_ALLOWED_ORIGINS=http://localhost:8083,http://localhost:3000
```

### Database Issues
```bash
# Reset database (development only)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 8083
lsof -ti:8083 | xargs kill -9
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Generate secure `SECRET_KEY`
3. Configure PostgreSQL database
4. Set up Redis for caching and WebSockets
5. Configure email settings
6. Set proper `ALLOWED_HOSTS`
7. Use HTTPS/SSL certificates
8. Run with Docker Compose or deploy to cloud platform

## Monitoring

Use the admin dashboard at `http://localhost:8083/pages/admin.html` for:
- Real-time server metrics
- User management
- Room management
- Message monitoring
- System health checks
- Activity logs

Or use the shell script:
```bash
./monitor.sh
```

## Additional Resources

- Full documentation: `README.md`
- Project overview: `PROJECT_README.md`
- API documentation: `http://localhost:8000/api/docs/`
