# Single Stage build using pre-built static assets
FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy pre-built frontend dist
COPY frontend/dist ./frontend/dist

# Expose port (Cloud Run defaults to 8080)
ENV PORT 8080
EXPOSE 8080

# Environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app:/app/backend

# Create data directory
RUN mkdir -p backend/data

# Start the application from the backend directory
WORKDIR /app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
