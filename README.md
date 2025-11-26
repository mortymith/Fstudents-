# Fstudents-

### Start Services

```bash
# Start all services in foreground
docker compose up

# Start all services in background (detached)
docker compose up -d

# Start specific services
docker compose up postgres redis

# Start with monitoring profiles
docker compose --profile monitoring up -d
```

### Stop Services

```bash
# Stop all running services
docker compose down

# Stop services and remove volumes (WARNING: deletes data)
docker compose down -v

# Stop specific services
docker compose stop postgres redis
```

### Restart Services

```bash
# Restart all services
docker compose restart

# Restart specific services
docker compose restart postgres

# Force recreate containers
docker compose up -d --force-recreate
```

### View Service Status

```bash
# List all containers
docker compose ps

# View running processes
docker compose top

# Check service logs
docker compose logs

# Follow logs in real-time
docker compose logs -f

# View logs for specific service
docker compose logs postgres
docker compose logs redis
```

### Container Information

```bash
# View detailed container info
docker compose inspect postgres

# Check health status
docker compose ps --services | xargs -I {} docker compose ps {}

# View resource usage
docker compose stats
```

## Database Operations

### PostgreSQL Access

```bash
# Connect to database
docker compose exec postgres psql postgresql://app_user:pass12345@127.0.0.1:5432/app_db

# Connect to PostgreSQL directly
docker compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB

# Run SQL file
docker compose exec -T postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -f /docker-entrypoint-initdb.d/your_script.sql

# Create database backup
docker compose exec -T postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup.sql
```

### Redis Operations

```bash
# Connect to Redis CLI
docker compose exec redis redis-cli -a $REDIS_PASSWORD

# Monitor Redis in real-time
docker compose exec redis redis-cli -a $REDIS_PASSWORD monitor

# Redis info and stats
docker compose exec redis redis-cli -a $REDIS_PASSWORD info
```

## Monitoring Tools

### Access Monitoring Interfaces

```bash
# PgAdmin (http://localhost:8080)
# Redis Commander (http://localhost:8081)

# Start only monitoring services
docker compose --profile monitoring up pgadmin redis-commander -d
```

## Maintenance and Cleanup

### Data Management

```bash
# Backup volumes
tar -czf backup_$(date +%Y%m%d).tar.gz data/

# Restore volumes
tar -xzf backup_20231201.tar.gz

# Clean up unused volumes
docker volume prune
```

### System Cleanup

```bash
# Remove all containers, networks, and images
docker compose down --rmi all --volumes

# Remove unused Docker objects
docker system prune

# Remove specific volumes
docker volume rm $(docker compose config --volumes)
```

## Development and Debugging

### Debug Commands

```bash
# Shell access to containers
docker compose exec postgres bash
docker compose exec redis sh

# View specific service logs with timestamps
docker compose logs -f --timestamps postgres

# Check service health
docker compose exec postgres pg_isready -U $POSTGRES_USER

# Test Redis connection
docker compose exec redis redis-cli -a $REDIS_PASSWORD ping
```

### Configuration Validation

```bash
# Validate compose file
docker compose config

# Dry run to see what would be created
docker compose up --dry-run

# List all services
docker compose config --services
```

## Service-Specific Management

### PostgreSQL Maintenance

```bash
# Check PostgreSQL configuration
docker compose exec postgres cat /bitnami/postgresql/conf/postgresql.conf

# Restart PostgreSQL with new config
docker compose restart postgres

# Check connection count
docker compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT count(*) FROM pg_stat_activity;"
```

### Redis Maintenance

```bash
# Flush Redis database
docker compose exec redis redis-cli -a $REDIS_PASSWORD FLUSHALL

# Save Redis data to disk
docker compose exec redis redis-cli -a $REDIS_PASSWORD SAVE

# Get Redis memory info
docker compose exec redis redis-cli -a $REDIS_PASSWORD INFO MEMORY
```

## Quick Reference - Common Workflows

### Development Startup

```bash

# 1. Start all services
docker compose up -d

# 2. Start monitoring tools
docker compose --profile monitoring up -d

# 3. Verify services
docker compose ps
```

### Production-like Setup

```bash
# Start core services only (no monitoring)
docker compose up -d postgres redis

# Check health status
docker compose ps
```

### Emergency Recovery

```bash
# Stop everything
docker compose down

# Restart with clean state (preserves data)
docker compose up --profile monitoring -d

# If having issues, rebuild
docker compose up -d --build
```
