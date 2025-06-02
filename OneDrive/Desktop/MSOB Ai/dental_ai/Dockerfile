# Use the official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy app files
COPY . .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Set environment variable to avoid Streamlit asking for config at runtime
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Expose the port Streamlit runs on
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app.py"]
