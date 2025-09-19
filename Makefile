# Loud Hawk v2 - Development Makefile
# Simplified commands for Docker management

.PHONY: help dev prod up down logs status build rebuild clean

# Default target
help:
	@echo "🚀 Loud Hawk v2 - Docker Management"
	@echo ""
	@echo "Available commands:"
	@echo "  dev      - Start development environment (with hot reload)"
	@echo "  prod     - Start production environment"
	@echo "  up       - Start services (production mode)"
	@echo "  down     - Stop all services"
	@echo "  logs     - Show logs for all services"
	@echo "  status   - Show service status"
	@echo "  build    - Build all images"
	@echo "  rebuild  - Rebuild all images (no cache)"
	@echo "  clean    - Stop services and clean up resources"
	@echo ""

# Development environment
dev:
	@echo "🚀 Starting Loud Hawk v2 Development Environment..."
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
	@echo "✅ Development environment started!"
	@echo "🌐 Frontend: http://localhost:5173"
	@echo "🔧 Backend API: http://localhost:8000"
	@echo "📚 API Docs: http://localhost:8000/docs"

# Production environment
prod:
	@echo "🚀 Starting Loud Hawk v2 Production Environment..."
	docker compose --profile production up --build -d
	@echo "✅ Production environment started!"
	@echo "🔧 Backend API: http://localhost:8000"
	@echo "📚 API Docs: http://localhost:8000/docs"

# Start services (production mode)
up:
	@echo "🚀 Starting Loud Hawk v2 Services..."
	docker compose up --build -d
	@echo "✅ Services started!"

# Stop all services
down:
	@echo "🛑 Stopping Loud Hawk v2 Services..."
	docker compose down
	@echo "✅ Services stopped!"

# Show logs
logs:
	@echo "📋 Showing Loud Hawk v2 logs..."
	docker compose logs -f --tail=200

# Show service status
status:
	@echo "📊 Loud Hawk v2 Service Status:"
	docker compose ps

# Build images
build:
	@echo "🔨 Building Loud Hawk v2 images..."
	docker compose build
	@echo "✅ Build complete!"

# Rebuild images (no cache)
rebuild:
	@echo "🔨 Rebuilding Loud Hawk v2 images (no cache)..."
	docker compose build --no-cache
	@echo "✅ Rebuild complete!"

# Clean up
clean:
	@echo "🧹 Cleaning up Loud Hawk v2 resources..."
	docker compose down -v
	docker system prune -f
	@echo "✅ Cleanup complete!"

# Development shortcuts
dev-logs:
	@echo "📋 Showing development logs..."
	docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f --tail=200

dev-status:
	@echo "📊 Development Service Status:"
	docker compose -f docker-compose.yml -f docker-compose.dev.yml ps

# Backend only
backend:
	@echo "🔧 Starting backend only..."
	docker compose up backend postgres redis --build -d
	@echo "✅ Backend started!"

# Frontend only (requires backend)
frontend:
	@echo "🌐 Starting frontend only..."
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up frontend --build -d
	@echo "✅ Frontend started!"
