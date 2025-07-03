FROM python:3.10-slim

# Set the working directory in the Docker container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install requirements 
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code
COPY . .

# Command to run your application
CMD ["python", "main.py"]