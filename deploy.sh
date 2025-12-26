#!/bin/bash

# MentorBot RAG Application Deployment Script
# Usage: ./deploy.sh [update|start|stop|restart|logs|status|rebuild]

set -e

APP_NAME="mentorbot-rag"
GIT_REPO="https://github.com/Shudi-Zhao/mentorbot.git"  # Set this on server or use SSH
APP_DIR="/var/www/mentorbot"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Function to check if app is running
check_status() {
    if docker-compose ps | grep -q "Up"; then
        return 0
    else
        return 1
    fi
}

# Function to update from git and redeploy
update_app() {
    print_status "Updating MentorBot application..."

    # Check if git repo is configured
    if [ -z "$GIT_REPO" ]; then
        print_warning "Git repo not configured. Skipping git pull."
    else
        print_status "Pulling latest changes from git..."
        git pull origin main
    fi

    # Rebuild and restart
    print_status "Building and starting containers..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d

    # Wait for health check
    print_status "Waiting for application to be healthy..."
    sleep 15

    # Check if container is running
    if check_status; then
        print_status "✅ Application updated successfully!"
        print_status "🌐 Available at: https://rag.shudizhao.com"
        print_status "📊 Local access: http://localhost:8503"
    else
        print_error "❌ Application failed to start. Check logs with: ./deploy.sh logs"
        exit 1
    fi
}

# Function to start the application
start_app() {
    print_status "Starting MentorBot application..."

    if check_status; then
        print_warning "Application is already running"
        return 0
    fi

    docker-compose up -d
    sleep 10

    if check_status; then
        print_status "✅ Application started successfully!"
        print_status "🌐 Available at: https://rag.shudizhao.com"
        print_status "📊 Local access: http://localhost:8503"
    else
        print_error "❌ Failed to start application"
        exit 1
    fi
}

# Function to stop the application
stop_app() {
    print_status "Stopping MentorBot application..."
    docker-compose down
    print_status "✅ Application stopped"
}

# Function to restart the application
restart_app() {
    print_status "Restarting MentorBot application..."
    docker-compose restart
    sleep 10

    if check_status; then
        print_status "✅ Application restarted successfully!"
        print_status "🌐 Available at: https://rag.shudizhao.com"
    else
        print_error "❌ Failed to restart application"
        exit 1
    fi
}

# Function to show logs
show_logs() {
    print_info "Showing logs (Ctrl+C to exit)..."
    docker-compose logs -f --tail=100
}

# Function to show status
show_status() {
    print_info "Container Status:"
    docker-compose ps
    echo ""

    if check_status; then
        print_status "✅ Application is running"
        print_info "🌐 URL: https://rag.shudizhao.com"
        print_info "📊 Local: http://localhost:8503"
    else
        print_warning "❌ Application is not running"
    fi
}

# Function to rebuild without cache
rebuild_app() {
    print_status "Rebuilding application from scratch..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    sleep 15

    if check_status; then
        print_status "✅ Application rebuilt successfully!"
    else
        print_error "❌ Failed to rebuild application"
        exit 1
    fi
}

# Main script logic
case "$1" in
    update)
        update_app
        ;;
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    rebuild)
        rebuild_app
        ;;
    *)
        echo "MentorBot RAG Application Deployment Manager"
        echo ""
        echo "Usage: $0 {update|start|stop|restart|logs|status|rebuild}"
        echo ""
        echo "Commands:"
        echo "  update  - Pull latest code and redeploy"
        echo "  start   - Start the application"
        echo "  stop    - Stop the application"
        echo "  restart - Restart the application"
        echo "  logs    - Show application logs (live)"
        echo "  status  - Show application status"
        echo "  rebuild - Rebuild containers from scratch"
        echo ""
        echo "Example: ./deploy.sh update"
        exit 1
        ;;
esac
