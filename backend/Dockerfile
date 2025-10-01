# Use an official Node.js runtime as a parent image
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install production dependencies using npm ci for reproducible builds
RUN npm ci --omit=dev

# Copy the rest of the application source code
COPY . .

# Create a non-root user and switch to it
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN chown -R appuser:appgroup /usr/src/app
USER appuser

# Make port 3001 available to the world outside this container
EXPOSE 3001

# Define the command to run the app
CMD [ "node", "src/index.js" ]
