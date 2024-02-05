#!/usr/bin/env bash
echo "Start service"

# migrate database
python scripts/migrate.py


exec uvicorn --factory app.main:create_app --host=$BIND_IP --port=$BIND_PORT --reload
