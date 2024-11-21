# Base image
FROM python:3.10

# Set working directory
WORKDIR /code

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy application files
COPY . .

# Expose the application port
EXPOSE 5000

# Run the Flask application
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]