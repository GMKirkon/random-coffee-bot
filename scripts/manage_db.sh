#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to start the database
start_db() {
    print_message "Starting MongoDB..."
    docker-compose up -d mongodb mongo-express
    print_message "Waiting for MongoDB to be ready..."
    sleep 5
    print_message "MongoDB is ready!"
    print_message "You can access Mongo Express at http://localhost:8081"
    print_message "Username: admin"
    print_message "Password: pass"
}

# Function to stop the database
stop_db() {
    print_message "Stopping MongoDB..."
    docker-compose stop mongodb mongo-express
    print_message "MongoDB stopped!"
}

# Function to restart the database
restart_db() {
    print_message "Restarting MongoDB..."
    docker-compose restart mongodb mongo-express
    print_message "MongoDB restarted!"
}

# Function to show database status
status_db() {
    print_message "Checking MongoDB status..."
    
    # Get container status
    container_status=$(docker-compose ps mongodb --format json | grep -o '"Status":"[^"]*"' | cut -d'"' -f4)
    
    if [ "$container_status" = "running (healthy)" ]; then
        print_message "MongoDB container is running and healthy"
        
        # Try to connect to MongoDB
        if docker-compose exec -T mongodb mongosh --eval "db.runCommand('ping').ok" > /dev/null 2>&1; then
            print_message "MongoDB is accepting connections"
        else
            print_message "MongoDB is running but not accepting connections"
        fi
    else
        print_message "MongoDB container status: $container_status"
        print_message "Current container details:"
        docker-compose ps mongodb
    fi
}

# Function to backup the database
backup_db() {
    print_message "Creating backup..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_dir="backups"
    mkdir -p $backup_dir
    
    docker-compose exec -T mongodb mongodump --out /data/backup
    docker cp $(docker-compose ps -q mongodb):/data/backup $backup_dir/backup_$timestamp
    print_message "Backup created in $backup_dir/backup_$timestamp"
}

# Function to restore the database
restore_db() {
    if [ -z "$1" ]; then
        print_error "Please provide a backup directory"
        print_message "Usage: $0 restore <backup_directory>"
        exit 1
    fi
    
    print_message "Restoring from backup..."
    docker cp $1 $(docker-compose ps -q mongodb):/data/backup
    docker-compose exec -T mongodb mongorestore /data/backup
    print_message "Backup restored!"
}

# Main script
check_docker

case "$1" in
    start)
        start_db
        ;;
    stop)
        stop_db
        ;;
    restart)
        restart_db
        ;;
    status)
        status_db
        ;;
    backup)
        backup_db
        ;;
    restore)
        restore_db $2
        ;;
    *)
        print_message "Usage: $0 {start|stop|restart|status|backup|restore}"
        print_message "  start   - Start MongoDB"
        print_message "  stop    - Stop MongoDB"
        print_message "  restart - Restart MongoDB"
        print_message "  status  - Check MongoDB status"
        print_message "  backup  - Create a backup"
        print_message "  restore - Restore from backup (requires backup directory)"
        exit 1
        ;;
esac 