# Migration from Redis to PostgreSQL

## Overview
This document describes the changes made to migrate the voting application from Redis to PostgreSQL.

## Changes Made

### 1. Docker Compose Configuration ([`docker-compose.yml`](docker-compose.yml))
- **Removed**: Redis service (port 6379)
- **Added**: PostgreSQL service with the following configuration:
  - Image: `postgres:15-alpine`
  - Database: `voting_db`
  - User: `voting_user`
  - Password: `voting_password`
  - Port: `5432:5432`
  - Volume: `postgres_data` for persistent storage
  - Initialization script: [`init_db.sql`](init_db.sql)
- **Updated**: `service_b` dependencies to use `postgres` instead of `redis`
- **Added**: Database connection environment variables to `service_b`:
  - `DB_HOST=postgres`
  - `DB_NAME=voting_db`
  - `DB_USER=voting_user`
  - `DB_PASSWORD=voting_password`

### 2. Service B Dependencies ([`service_b/requirements.txt`](service_b/requirements.txt))
- **Removed**: `redis` package
- **Added**: `psycopg2-binary` package for PostgreSQL connectivity

### 3. Service B Application ([`service_b/app.py`](service_b/app.py))
- **Removed**: Redis client initialization
- **Added**: PostgreSQL connection management with `psycopg2`
- **Updated**: [`vote()`](service_b/app.py:24) endpoint to use SQL UPSERT for vote counting
- **Updated**: [`results()`](service_b/app.py:48) endpoint to query PostgreSQL database
- **Added**: Proper connection handling with try/finally blocks
- **Added**: Database connection function [`get_db_connection()`](service_b/app.py:13)

### 4. Database Initialization ([`init_db.sql`](init_db.sql))
- **Created**: New SQL initialization script that runs automatically on PostgreSQL startup
- **Features**:
  - Creates `votes` table with `option_name` (primary key) and `vote_count` columns
  - Adds index on `option_name` for faster lookups
  - Includes timestamp tracking (`created_at`, `updated_at`)
  - Implements trigger to auto-update `updated_at` timestamp

## Database Schema

### Table: `votes`
| Column | Type | Description |
|--------|------|-------------|
| `option_name` | VARCHAR(255) | Primary key, stores the voting option name |
| `vote_count` | INTEGER | Number of votes for this option |
| `created_at` | TIMESTAMP | When the option was first created |
| `updated_at` | TIMESTAMP | Last time the vote count was updated |

## How It Works

### Voting Process
1. User submits a vote via the frontend
2. [`service_b/app.py`](service_b/app.py) receives the vote request
3. Application connects to PostgreSQL
4. Uses SQL UPSERT to either:
   - Insert new option with count = 1, or
   - Increment existing option's vote count
5. Commits transaction and closes connection

### Results Retrieval
1. Frontend requests current results
2. [`service_b/app.py`](service_b/app.py) queries PostgreSQL for both options
3. Returns vote counts in JSON format
4. Frontend displays results to user

## Advantages of PostgreSQL over Redis

1. **Persistence**: Data is stored on disk and survives container restarts
2. **ACID Compliance**: Transactions ensure data integrity
3. **SQL Support**: Complex queries and reporting capabilities
4. **Scalability**: Better suited for large-scale applications
5. **Backup/Restore**: Standard database backup tools available
6. **Data Relationships**: Can easily extend to support more complex data models

## Running the Application

### Start the application:
```bash
docker-compose up -d
```

### Stop the application:
```bash
docker-compose down
```

### Stop and remove volumes (clear all data):
```bash
docker-compose down -v
```

### View logs:
```bash
docker-compose logs -f service_b
docker-compose logs -f postgres
```

### Access PostgreSQL directly:
```bash
docker-compose exec postgres psql -U voting_user -d voting_db
```

### Query the database:
```sql
SELECT * FROM votes;
```

## Environment Variables

### PostgreSQL Configuration
- `DB_HOST`: PostgreSQL host (default: `postgres`)
- `DB_NAME`: Database name (default: `voting_db`)
- `DB_USER`: Database user (default: `voting_user`)
- `DB_PASSWORD`: Database password (default: `voting_password`)

### Voting Options
- `OPTION_A`: First voting option (default: `Cats`)
- `OPTION_B`: Second voting option (default: `Dogs`)

## Troubleshooting

### Connection Issues
If `service_b` cannot connect to PostgreSQL:
1. Check if PostgreSQL is running: `docker-compose ps postgres`
2. Check logs: `docker-compose logs postgres`
3. Verify environment variables in [`docker-compose.yml`](docker-compose.yml)

### Database Not Initializing
If the database schema is not created:
1. Check [`init_db.sql`](init_db.sql) exists in the project root
2. Verify volume mount in [`docker-compose.yml`](docker-compose.yml)
3. Remove volumes and restart: `docker-compose down -v && docker-compose up -d`

### Performance Considerations
- PostgreSQL connections are more expensive than Redis
- Consider using connection pooling for high-traffic scenarios
- The current implementation creates a new connection per request
- For production, consider using `psycopg2.pool` or SQLAlchemy

## Future Enhancements

1. **Connection Pooling**: Implement connection pooling for better performance
2. **ORM Integration**: Use SQLAlchemy for easier database management
3. **Additional Features**: Add vote history, timestamps per vote, user tracking
4. **Backup Strategy**: Implement automated database backups
5. **Migration Scripts**: Add versioned database migrations
6. **Monitoring**: Add database performance metrics to Prometheus
