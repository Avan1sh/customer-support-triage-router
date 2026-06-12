# syntax=docker/dockerfile:1

# Slim Python base - small, official, matches our dev Python (3.13).
FROM python:3.13-slim

# PYTHONDONTWRITEBYTECODE: don't litter .pyc files
# PYTHONUNBUFFERED: stream logs immediately (don't buffer stdout)
# PYTHONPATH: so 'import app...' works without juggling env vars at runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    HF_HUB_DISABLE_SYMLINKS_WARNING=1

WORKDIR /app

# 1) Install CPU-only PyTorch FIRST, from PyTorch's CPU wheel index.
#    The default torch pulls multi-GB CUDA libs we don't need for inference;
#    the CPU build keeps the image far smaller.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# 2) Copy ONLY requirements first, then install. This is Docker LAYER CACHING:
#    as long as requirements.txt is unchanged, this expensive layer is reused
#    even when you edit application code -> rebuilds become seconds, not minutes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Bake the embedding model into the image so the container never downloads
#    it at runtime (works offline; fast first request).
RUN python -c "from langchain_huggingface import HuggingFaceEmbeddings; HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')"

# 4) Now copy the app code (changes here don't bust the dependency cache above).
COPY app/ ./app/

# 5) Run as a NON-ROOT user - if the app is compromised, the attacker isn't root.
RUN useradd --create-home appuser && mkdir -p /app/store && chown -R appuser /app
USER appuser

EXPOSE 8000

# Docker can poll this to know whether the container is actually serving.
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# 0.0.0.0 (not 127.0.0.1) so the server is reachable from OUTSIDE the container.
CMD ["python", "-m", "uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
