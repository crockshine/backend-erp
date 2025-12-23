#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
# Wait for PostgreSQL to be ready
until python -c "
import asyncpg
import asyncio
import sys
import os

async def check_db():
    try:
        conn = await asyncpg.connect(
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DATABASE'),
            host=os.getenv('POSTGRES_HOST'),
            port=int(os.getenv('POSTGRES_PORT'))
        )
        await conn.close()
        return True
    except Exception as e:
        print(f'Database not ready yet: {e}', file=sys.stderr)
        return False

result = asyncio.run(check_db())
sys.exit(0 if result else 1)
" 2>/dev/null; do
    echo "Waiting for database..."
    sleep 2
done

echo "PostgreSQL is ready!"

echo "Environment variables check:"
echo "POSTGRES_HOST: $POSTGRES_HOST"
echo "POSTGRES_USER: $POSTGRES_USER"
echo "POSTGRES_DATABASE: $POSTGRES_DATABASE"

echo "Running Alembic migrations to create tables..."
cd /app
alembic upgrade head

echo "Seeding admin user..."
python -m seed_admin

echo "Starting FastAPI application..."
exec uvicorn src.main:app --reload --host 0.0.0.0 --port 8008


