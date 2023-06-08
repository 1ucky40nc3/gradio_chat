FROM python:3.11-slim-bullseye AS compile-image
RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc

WORKDIR /app

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY README.md .
COPY setup.py .
COPY src/ src/
RUN python3 -m pip install -e .

FROM python:3.11-slim-bullseye AS build-image

WORKDIR /app

COPY --from=compile-image /app/src /app/src
COPY --from=compile-image /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
CMD ["python3", "src/frontend/app.py", "--server_name", "0.0.0.0"]