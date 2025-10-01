# Stage 1: Build the VitePress site
FROM node:20-slim as builder
WORKDIR /app

# Install security updates and clean cache
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies (prefer npm ci for reproducibility)
RUN npm ci

# Copy the docs directory
COPY docs/ ./docs/

# Build the VitePress site
RUN npm run docs:build

# Stage 2: Serve the static files with Nginx
FROM nginx:1.27.2-alpine3.20

WORKDIR /usr/share/nginx/html

# Remove default Nginx public folder
RUN rm -rf ./*

# Copy the built site from the builder stage (VitePress builds to docs/.vitepress/dist)
COPY --from=builder /app/docs/.vitepress/dist/ .

# Copy the Nginx configuration
COPY docs/nginx.conf /etc/nginx/conf.d/default.conf

# Drop privileges for security
RUN adduser -D appuser && chown -R appuser:appuser /usr/share/nginx/html
USER appuser

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
