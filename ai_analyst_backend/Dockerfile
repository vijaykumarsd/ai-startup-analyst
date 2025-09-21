# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container
COPY . .

# Expose the port that Uvicorn will run on
ENV PORT 8080
EXPOSE $PORT

# Run the application using Uvicorn
# The --host 0.0.0.0 is important for Cloud Run to correctly route traffic
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
