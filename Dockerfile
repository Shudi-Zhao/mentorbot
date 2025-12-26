# MentorBot RAG Application Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY demo_content/ ./demo_content/

# Create directories for persistent storage
RUN mkdir -p /app/data/uploads /app/data/chroma_db /app/logs

# Expose port for Streamlit
EXPOSE 8503

# Health check using Streamlit health endpoint
HEALTHCHECK CMD curl --fail http://localhost:8503/_stcore/health

# Run the MentorBot application
ENTRYPOINT ["streamlit", "run", "app/main.py", \
    "--server.port=8503", \
    "--server.address=0.0.0.0", \
    "--browser.serverAddress=rag.shudizhao.com", \
    "--server.headless=true", \
    "--browser.gatherUsageStats=false"]
