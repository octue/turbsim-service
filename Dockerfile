FROM octue/openfast

COPY requirements-dev.txt .
COPY . .

RUN pip3 install -r requirements-dev.txt

EXPOSE $PORT

ARG _SERVICE_ID
ENV SERVICE_ID=$_SERVICE_ID

ARG _GUNICORN_WORKERS=1
ENV _GUNICORN_WORKERS=$_GUNICORN_WORKERS

ARG _GUNICORN_THREADS=8
ENV _GUNICORN_THREADS=$_GUNICORN_THREADS

# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers $_GUNICORN_WORKERS --threads $_GUNICORN_THREADS --timeout 0 octue.cloud.deployment.google.cloud_run:app
