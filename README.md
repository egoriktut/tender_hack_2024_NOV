# to run type check
mypy app/

## Prerequisites

1. **Python 3.8+** - Make sure Python and pip are installed.
2. **Redis** - Celery uses Redis as the message broker. Install it locally or use a Redis instance in the cloud.


python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
redis-server
celery -A app.celery_app worker --loglevel=debug

фастапи поднять
uvicorn app.main:app --reload --host 0.0.0.0 --port 8090


тупо баш, над[README.md](README.md)еемся что сразуу стартанет
./run.sh




для винды лохов надо подргомуу
celery -A app.celery_app worker --pool=solo --loglevel=info

