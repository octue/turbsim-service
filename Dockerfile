FROM octue/openfast

# Allow statements and log messages to immediately appear in the Knative logs on Google Cloud.
ENV PYTHONUNBUFFERED True

ENV PROJECT_ROOT=/app
WORKDIR $PROJECT_ROOT

COPY requirements-dev.txt .
COPY . .

RUN pip3 install -r requirements-dev.txt

EXPOSE $PORT

ENV USE_OCTUE_LOG_HANDLER=1
ENV COMPUTE_PROVIDER=GOOGLE_CLOUD_RUN

ARG SERVICE_ID
ENV SERVICE_ID=$SERVICE_ID

ARG GUNICORN_WORKERS=1
ENV GUNICORN_WORKERS=$GUNICORN_WORKERS

ARG GUNICORN_THREADS=8
ENV GUNICORN_THREADS=$GUNICORN_THREADS

# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers $GUNICORN_WORKERS --threads $GUNICORN_THREADS --timeout 0 octue.cloud.deployment.google.cloud_run:app
