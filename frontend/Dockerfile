# Multi-stage build for production-ready frontend
FROM nginx:alpine AS production

# Copy built assets
COPY . /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

# Development stage
FROM node:18-alpine AS development

WORKDIR /app

# Copy source files
COPY . .

# Install serve for development
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Start development server
CMD ["serve", ".", "-l", "3000", "-s"]
