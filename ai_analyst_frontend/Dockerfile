# Use a Node.js base image to build the React app
FROM node:18-alpine as builder

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to install dependencies
COPY package.json ./
COPY package-lock.json ./

# Install dependencies using npm ci for clean install
RUN npm ci

# Copy the rest of the application code
COPY . .

# Build the React app for production
RUN npm run build

# --- DIAGNOSTIC STEP: List contents of /app after build ---
RUN ls -la /app
RUN ls -la /app/build || echo "/app/build does not exist or is empty"
# ---------------------------------------------------------

# Use a lightweight Nginx image to serve the static files
FROM nginx:stable-alpine

# Copy the built React app from the builder stage to Nginx's html directory
COPY --from=builder /app/build /usr/share/nginx/html

# Remove default Nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 (default for Nginx)
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
