# Use an official lightweight Node.js image
FROM node:20-slim

# Set the working directory in the container
WORKDIR /app

# Copy dependency configuration files
COPY package*.json ./

# Install dependencies
RUN npm install --no-audit --no-fund

# Copy the application source code
COPY . .

# Expose the port for Vite
EXPOSE 5173

# Start the application in development mode
CMD ["npm", "run", "dev"]
