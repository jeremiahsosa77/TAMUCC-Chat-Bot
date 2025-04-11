FROM node:16-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the application
COPY . .

# Build the application
RUN npm run build

# Install serve to run the application
RUN npm install -g serve

# Expose the port
EXPOSE 3000

# Command to run the application
CMD ["serve", "-s", "build", "-l", "3000"] 