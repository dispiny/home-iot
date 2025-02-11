# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install werkzeug
# Expose the port that Flask will run on
EXPOSE 5000

# Define environment variables
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Run the Flask app
CMD ["flask", "run"]
