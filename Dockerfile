FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "--worker-class", "uvicorn.workers.UvicornWorker", "app.main:app"]
