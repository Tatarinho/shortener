# Use an official lightweight Python image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install Poetry globally
RUN pip install --no-cache-dir poetry

# Copy configuration files for Poetry
COPY pyproject.toml poetry.lock ./

# Configure Poetry to install dependencies without creating a virtual environment in the container
RUN poetry config virtualenvs.create false \
    && poetry install --without dev --no-interaction --no-ansi


# Copy the application code into the container
COPY . .

# Expose the port on which FastAPI will run
EXPOSE 8000

# Run the FastAPI application
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
