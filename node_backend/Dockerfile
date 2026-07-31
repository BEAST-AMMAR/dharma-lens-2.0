FROM node:20-alpine

WORKDIR /app

# Copy dependency definitions
COPY package*.json ./

# Install production dependencies
RUN npm ci --only=production

# Copy application source code
COPY . .

# Expose API gateway port
EXPOSE 3000

# Start server
CMD ["npm", "start"]
