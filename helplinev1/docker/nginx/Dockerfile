# Nginx Dockerfile
FROM nginx:alpine

# Remove default nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration files
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./helpline.conf /etc/nginx/conf.d/helpline.conf


# Create necessary directories
RUN mkdir -p /var/www/html/helpline

# Create self-signed SSL certificate for development
RUN apk add --no-cache openssl && \
    mkdir -p /etc/ssl/certs && \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/certs/helpline.key \
    -out /etc/ssl/certs/helpline.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Set proper permissions
RUN chown -R nginx:nginx /var/www/html

# Expose ports
EXPOSE 80 443

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]