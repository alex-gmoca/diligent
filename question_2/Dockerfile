FROM python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    unzip && \
    rm -rf /var/lib/apt/lists/*

# Add execution script
COPY executor.py /app/executor.py

# Entry point for execution
ENTRYPOINT ["python", "executor.py"]
