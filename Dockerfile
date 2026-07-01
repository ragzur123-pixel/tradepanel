# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install a cron daemon if we want to run the worker internally, 
# or we can rely on a cloud scheduler like Heroku Scheduler / Render Cron.
# For simplicity, we will run the worker as a continuous loop using a python scheduler.
RUN pip install schedule

# Copy the rest of the application
COPY src/ src/
COPY .env .env

# Copy the intraday runner script
COPY cloud_runner.py .

# Run cloud_runner.py when the container launches
CMD ["python", "cloud_runner.py"]
