FROM python:3.13-slim

# Install pandoc for the docgen tool to function correctly
RUN apt-get update && apt-get install -y pandoc && rm -rf /var/lib/apt/lists/*

# Pull uv directly from Astral's official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy the entire project into the container
COPY . .

# Sync the exact dependencies using uv
RUN uv sync --all-extras

EXPOSE 8501

# Tell the Ollama Python client to look for the host machine's Ollama, not inside the container
ENV OLLAMA_HOST=http://host.docker.internal:11434

# Launch Streamlit
CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
