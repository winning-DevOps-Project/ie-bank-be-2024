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

# Run database migrations and then start the application
CMD ["bash", "-c", "flask db upgrade && python3 create_admin.py && python3 -m flask run --host=0.0.0.0"]
