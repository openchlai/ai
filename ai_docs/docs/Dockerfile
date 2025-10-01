# Stage 1: Build the VitePress site
FROM node:20-alpine as builder
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the docs directory
COPY docs/ ./docs/

# Build the VitePress site
RUN npm run docs:build

# Stage 2: Serve the static files with Nginx
FROM nginx:alpine
WORKDIR /usr/share/nginx/html

# Remove default Nginx public folder
RUN rm -rf ./*

# Copy the built site from the builder stage (VitePress builds to docs/.vitepress/dist)
COPY --from=builder /app/docs/.vitepress/dist/ .

# Copy the Nginx configuration
COPY docs/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
