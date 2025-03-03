FROM ghcr.io/openfast/openfast:3.5.3

# Allow statements and log messages to immediately appear in the Knative logs on Google Cloud.
ENV PYTHONUNBUFFERED True

ENV PROJECT_ROOT=/workspace
WORKDIR $PROJECT_ROOT

RUN apt-get update -y && apt-get install -y --fix-missing curl python3.11 && rm -rf /var/lib/apt/lists/*

# Install poetry.
ENV POETRY_HOME=/root/.poetry
ENV PATH "$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3.11 - && poetry config virtualenvs.create false;

# Copy in dependency files for caching.
COPY pyproject.toml poetry.lock ./

# Install just the dependencies to utilise layer caching for quick rebuilds.
RUN poetry install  \
    --no-ansi  \
    --no-interaction  \
    --no-cache  \
    --no-root  \
    --only main

COPY . .

# Install local packages.
RUN poetry install --only main

ENV USE_OCTUE_LOG_HANDLER=1
ENV COMPUTE_PROVIDER=GOOGLE_KUEUE
CMD ["octue", "question", "ask", "local"]
