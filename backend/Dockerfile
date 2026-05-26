FROM python:3.10-slim

WORKDIR /workspace

# Install essential build dependencies for scientific python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies list and install
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend folder (context should be run from root of project)
COPY backend/ /workspace/backend

# Expose FastAPI port
EXPOSE 8000

# Set PYTHONPATH so python can resolve from backend.xxxx imports
ENV PYTHONPATH=/workspace
ENV PORT=8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
