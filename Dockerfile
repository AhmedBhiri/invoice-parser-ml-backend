
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Install the required dependencies for the application

# Fixed typo: removed "sudo" from each line, as "apt-get" does not require sudo
RUN apt-get update \
    && apt-get install -y tesseract-ocr \ 
    && apt-get install -y libtesseract-dev \ 
    && apt-get install -y build-essential \  
    && apt-get install -y libpq-dev \ 
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file to the working directory
COPY requirements.txt requirements.txt

# Install the Python dependencies from the requirements.txt file
RUN pip3 install -r requirements.txt

# Copy the application code to the working directory
COPY . .

# Expose port 8000 for the application
EXPOSE 8000

# Set the command to run the application when the container starts
CMD [ "python3", "manage.py", "runserver", "0.0.0.0:8000"]
