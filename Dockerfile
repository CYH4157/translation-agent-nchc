FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /translation-agent-nchc

# Copy the entire project directory to the container's working directory
COPY . .

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install Poetry and ffmpy using pip
RUN pip install poetry ffmpy

# Install Python dependencies specified in the pyproject.toml file using Poetry
RUN poetry install --with app

# Add the startup script to the container
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Set the default command to run the startup script when the container starts
CMD ["/start.sh"]

# Expose the port for the application (if needed)
EXPOSE 7860
