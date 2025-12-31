FROM --platform=linux/arm64 python:3.12-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agents/ ./agents/
COPY tools/ ./tools/
COPY main.py .

# Expose port for A2A protocol
EXPOSE 9000

# Run the agent
CMD ["python", "main.py"]
