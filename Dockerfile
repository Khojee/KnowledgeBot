# Stage 1: Use an official Python runtime as a parent image
FROM python:3.11-slim

# Stage 2: Set the working directory inside the container
WORKDIR /app

# Stage 3: Copy the dependencies file and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 4: Copy the rest of the application's source code
COPY . .

# Stage 5: Define the command to run the application
CMD ["python", "main.py"]