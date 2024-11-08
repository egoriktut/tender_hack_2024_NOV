
### `run.sh` Script

This script will automate the steps for starting Redis, the Celery worker, and the FastAPI server. Ensure the script has executable permissions (`chmod +x run.sh`).

```bash
#!/bin/bash

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Start Redis (in the background if not already running)
if ! pgrep -x "redis-server" > /dev/null
then
    echo "Starting Redis server..."
    redis-server --daemonize yes
else
    echo "Redis server is already running."
fi

# Start Celery worker in a separate terminal
echo "Starting Celery worker..."
gnome-terminal -- bash -c "celery -A app.celery_app worker --loglevel=info"

# Start FastAPI application in another separate terminal
echo "Starting FastAPI server..."
gnome-terminal -- bash -c "uvicorn app.main:app --reload"

echo "All services are up and running."
