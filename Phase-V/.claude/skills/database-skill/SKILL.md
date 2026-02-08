---
name: database-skill
description: Manage databases, migrations, backups, optimization, and data persistence. Use for database operations and data management.
---

# Database Skill - Management, Migrations & Optimization

## Instructions

1. **Database Selection & Setup**
   - Choose appropriate database type (SQL vs NoSQL)
   - PostgreSQL: Relational data, ACID compliance, complex queries
   - MongoDB: Flexible schemas, document storage, rapid iteration
   - Redis: Caching, sessions, real-time data
   - MySQL: Traditional relational, wide hosting support
   - Set up proper connection pooling
   - Configure SSL/TLS for connections

2. **Schema Design & Migrations**
   - Design normalized schemas for relational databases
   - Create migration files with up/down functions
   - Use migration tools (Prisma, TypeORM, Sequelize, Alembic, Flyway)
   - Version control all schema changes
   - Test migrations in development before production
   - Never modify production schema manually
   - Include rollback strategies

3. **Query Optimization**
   - Create indexes on frequently queried columns
   - Use EXPLAIN/ANALYZE to identify slow queries
   - Avoid N+1 query problems
   - Use connection pooling efficiently
   - Implement query result caching where appropriate
   - Batch operations when possible
   - Use prepared statements for security and performance

4. **Backup & Recovery**
   - Schedule automated backups (daily minimum for production)
   - Test backup restoration regularly
   - Use point-in-time recovery when available
   - Store backups in separate location/region
   - Implement backup retention policies
   - Document recovery procedures

5. **Security & Access Control**
   - Use least-privilege principle for database users
   - Never use root/admin credentials in applications
   - Encrypt sensitive data at rest
   - Use SSL/TLS for data in transit
   - Implement row-level security where needed
   - Rotate database credentials regularly
   - Sanitize all user inputs (prevent SQL injection)

6. **Monitoring & Performance**
   - Monitor connection pool usage
   - Track slow query logs
   - Set up alerts for high CPU/memory usage
   - Monitor disk space and growth trends
   - Track replication lag (if using replicas)
   - Monitor cache hit ratios

## Best Practices

- **Environment Parity**: Keep dev/staging/prod schemas synchronized
- **Data Integrity**: Use foreign keys, constraints, and validations
- **Transactions**: Use transactions for multi-step operations
- **Idempotency**: Make migrations idempotent (safe to run multiple times)
- **Documentation**: Document schema changes and their purpose
- **Testing**: Test database operations with realistic data volumes
- **Audit Logging**: Track who changed what and when
- **Graceful Degradation**: Handle database unavailability gracefully

## Example Configurations

### PostgreSQL with Prisma

#### Prisma Schema (schema.prisma)
```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  posts     Post[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@index([email])
}

model Post {
  id        String   @id @default(cuid())
  title     String
  content   String?
  published Boolean  @default(false)
  author    User     @relation(fields: [authorId], references: [id])
  authorId  String
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@index([authorId])
  @@index([published])
}
```

#### Migration Example
```typescript
// migrations/20240115_add_user_role.ts
import { Prisma } from '@prisma/client';

export async function up(prisma: Prisma.TransactionClient) {
  await prisma.$executeRaw`
    ALTER TABLE "User" 
    ADD COLUMN "role" TEXT NOT NULL DEFAULT 'user';
  `;
  
  await prisma.$executeRaw`
    CREATE INDEX "User_role_idx" ON "User"("role");
  `;
}

export async function down(prisma: Prisma.TransactionClient) {
  await prisma.$executeRaw`
    DROP INDEX IF EXISTS "User_role_idx";
  `;
  
  await prisma.$executeRaw`
    ALTER TABLE "User" 
    DROP COLUMN "role";
  `;
}
```

#### Database Connection with Pooling
```typescript
// lib/db.ts
import { PrismaClient } from '@prisma/client';

const globalForPrisma = global as unknown as { prisma: PrismaClient };

export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
    datasources: {
      db: {
        url: process.env.DATABASE_URL,
      },
    },
  });

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;

// Graceful shutdown
process.on('beforeExit', async () => {
  await prisma.$disconnect();
});
```

### MongoDB with Mongoose

#### Schema Definition
```typescript
// models/User.ts
import mongoose, { Schema, Document } from 'mongoose';

export interface IUser extends Document {
  email: string;
  name: string;
  posts: mongoose.Types.ObjectId[];
  createdAt: Date;
  updatedAt: Date;
}

const UserSchema = new Schema<IUser>(
  {
    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      trim: true,
      index: true,
    },
    name: {
      type: String,
      required: true,
      trim: true,
    },
    posts: [{
      type: Schema.Types.ObjectId,
      ref: 'Post',
    }],
  },
  {
    timestamps: true,
  }
);

// Compound index for common queries
UserSchema.index({ email: 1, createdAt: -1 });

export const User = mongoose.model<IUser>('User', UserSchema);
```

#### Connection Management
```typescript
// lib/mongodb.ts
import mongoose from 'mongoose';

const MONGODB_URI = process.env.MONGODB_URI!;

if (!MONGODB_URI) {
  throw new Error('Please define MONGODB_URI environment variable');
}

interface MongooseCache {
  conn: typeof mongoose | null;
  promise: Promise<typeof mongoose> | null;
}

declare global {
  var mongoose: MongooseCache;
}

let cached = global.mongoose;

if (!cached) {
  cached = global.mongoose = { conn: null, promise: null };
}

export async function connectDB() {
  if (cached.conn) {
    return cached.conn;
  }

  if (!cached.promise) {
    const opts = {
      bufferCommands: false,
      maxPoolSize: 10,
      minPoolSize: 2,
      socketTimeoutMS: 45000,
      serverSelectionTimeoutMS: 5000,
    };

    cached.promise = mongoose.connect(MONGODB_URI, opts);
  }

  try {
    cached.conn = await cached.promise;
  } catch (e) {
    cached.promise = null;
    throw e;
  }

  return cached.conn;
}
```

### Database Backup Script

#### PostgreSQL Backup
```bash
#!/bin/bash
# backup-postgres.sh

set -e

# Configuration
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-myapp}"
DB_USER="${DB_USER:-postgres}"
BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS=7

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Generate backup filename with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz"

# Perform backup
echo "Starting backup of $DB_NAME..."
PGPASSWORD="$DB_PASSWORD" pg_dump \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -F c \
  "$DB_NAME" | gzip > "$BACKUP_FILE"

# Verify backup
if [ -f "$BACKUP_FILE" ]; then
  BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
  echo "Backup completed: $BACKUP_FILE ($BACKUP_SIZE)"
else
  echo "Backup failed!"
  exit 1
fi

# Upload to S3 (optional)
if [ -n "$S3_BUCKET" ]; then
  aws s3 cp "$BACKUP_FILE" "s3://$S3_BUCKET/backups/postgres/"
  echo "Backup uploaded to S3"
fi

# Clean up old backups
find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -mtime +$RETENTION_DAYS -delete
echo "Cleaned up backups older than $RETENTION_DAYS days"

echo "Backup process completed successfully"
```

#### MongoDB Backup
```bash
#!/bin/bash
# backup-mongodb.sh

set -e

# Configuration
MONGO_URI="${MONGO_URI:-mongodb://localhost:27017}"
DB_NAME="${DB_NAME:-myapp}"
BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS=7

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Generate backup filename with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_PATH="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}"

# Perform backup
echo "Starting backup of $DB_NAME..."
mongodump \
  --uri="$MONGO_URI" \
  --db="$DB_NAME" \
  --out="$BACKUP_PATH" \
  --gzip

# Create archive
cd "$BACKUP_DIR"
tar -czf "${DB_NAME}_${TIMESTAMP}.tar.gz" "${DB_NAME}_${TIMESTAMP}"
rm -rf "${DB_NAME}_${TIMESTAMP}"

BACKUP_FILE="${DB_NAME}_${TIMESTAMP}.tar.gz"
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "Backup completed: $BACKUP_FILE ($BACKUP_SIZE)"

# Upload to S3 (optional)
if [ -n "$S3_BUCKET" ]; then
  aws s3 cp "$BACKUP_FILE" "s3://$S3_BUCKET/backups/mongodb/"
  echo "Backup uploaded to S3"
fi

# Clean up old backups
find "$BACKUP_DIR" -name "${DB_NAME}_*.tar.gz" -mtime +$RETENTION_DAYS -delete
echo "Cleaned up backups older than $RETENTION_DAYS days"

echo "Backup process completed successfully"
```

### Query Optimization Examples

#### Finding Slow Queries (PostgreSQL)
```sql
-- Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 1000; -- Log queries > 1 second
SELECT pg_reload_conf();

-- Find slow queries
SELECT 
  query,
  calls,
  total_exec_time,
  mean_exec_time,
  max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Analyze query performance
EXPLAIN ANALYZE
SELECT u.*, COUNT(p.id) as post_count
FROM users u
LEFT JOIN posts p ON u.id = p.author_id
WHERE u.created_at > NOW() - INTERVAL '30 days'
GROUP BY u.id;
```

#### Creating Effective Indexes
```sql
-- Before: Slow query
SELECT * FROM posts WHERE author_id = '123' AND published = true;

-- Create composite index
CREATE INDEX idx_posts_author_published ON posts(author_id, published);

-- Verify index usage
EXPLAIN SELECT * FROM posts WHERE author_id = '123' AND published = true;

-- Create partial index (for specific conditions)
CREATE INDEX idx_published_posts ON posts(created_at) 
WHERE published = true;

-- Create index for text search
CREATE INDEX idx_posts_content_search ON posts 
USING gin(to_tsvector('english', content));
```

### Docker Compose for Databases
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: postgres-db
    environment:
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-password}
      POSTGRES_DB: ${DB_NAME:-myapp}
      PGDATA: /var/lib/postgresql/data/pgdata
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  mongodb:
    image: mongo:7
    container_name: mongodb
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_USER:-admin}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD:-password}
      MONGO_INITDB_DATABASE: ${MONGO_DB:-myapp}
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
      - ./mongo-init:/docker-entrypoint-initdb.d
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: redis-cache
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-password}
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    restart: unless-stopped

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: ${PGADMIN_EMAIL:-admin@admin.com}
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_PASSWORD:-admin}
    ports:
      - "5050:80"
    volumes:
      - pgadmin_data:/var/lib/pgadmin
    depends_on:
      - postgres
    restart: unless-stopped

volumes:
  postgres_data:
  mongodb_data:
  redis_data:
  pgadmin_data:
```