# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables 
# This is temporary, we'll change to secrets manager / docker secrets in production
ENV AWS_SECRET_ACCESS_KEY_FILE=/run/secrets/aws_secret_access_key \
    AWS_ACCESS_KEY_ID_FILE=/run/secrets/aws_access_key_id \
    S3_BUCKET_NAME_FILE=/run/secrets/s3_bucket_name \
    AWS_REGION_FILE=/run/secrets/aws_region \
    MONGO_URI_FILE=/run/secrets/mongo_uri \
    MONGO_DB_NAME_FILE=/run/secrets/mongo_db_name \
    MONGO_COLLECTION_NAME_FILE=/run/secrets/mongo_collection_name \
    SENDGRID_API_KEY_FILE=/run/secrets/sendgrid_api_key \
    PYTHONUNBUFFERED=1

# Set the working directory to /app 
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define a health check for the container
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Run app.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
