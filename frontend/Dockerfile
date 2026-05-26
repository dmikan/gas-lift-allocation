FROM python:3.10-slim

WORKDIR /workspace

# Copy dependencies list and install
COPY frontend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the frontend folder (context should be run from root of project)
COPY frontend/ /workspace/frontend

# Expose Streamlit port
EXPOSE 8501

# Set PYTHONPATH
ENV PYTHONPATH=/workspace

# Streamlit-specific configurations for running inside containers
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
