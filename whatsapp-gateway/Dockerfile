FROM node:20-slim

# Install system dependencies required for Baileys/Node
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    make \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --production

# Copy source code
COPY src ./src

# Create sessions directory
RUN mkdir -p sessions

# Expose port
EXPOSE 3000

# Start server
CMD ["npm", "start"]
