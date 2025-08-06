# PHP-FPM Dockerfile for Backend API
FROM php:8.2-fpm

# Install required system packages and PHP extensions
RUN apt-get update && apt-get install -y \
    libzip-dev \
    zip \
    unzip \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libonig-dev \
    libxml2-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j$(nproc) \
        mysqli \
        pdo \
        pdo_mysql \
        zip \
        gd \
        mbstring \
        xml \
        opcache \
    && rm -rf /var/lib/apt/lists/*

# Configure PHP-FPM pool
RUN echo "listen = 9000" >> /usr/local/etc/php-fpm.d/zz-docker.conf && \
    echo "pm.max_children = 50" >> /usr/local/etc/php-fpm.d/zz-docker.conf && \
    echo "pm.start_servers = 5" >> /usr/local/etc/php-fpm.d/zz-docker.conf && \
    echo "pm.min_spare_servers = 5" >> /usr/local/etc/php-fpm.d/zz-docker.conf && \
    echo "pm.max_spare_servers = 35" >> /usr/local/etc/php-fpm.d/zz-docker.conf

# Set working directory
WORKDIR /var/www/html

# Copy PHP configuration
COPY docker/php/php.ini /usr/local/etc/php/conf.d/custom.ini

# Create data directory and set permissions
RUN mkdir -p /var/www/html/helpline/data && \
    chown -R www-data:www-data /var/www/html

# Expose PHP-FPM port
EXPOSE 9000

# Start PHP-FPM
CMD ["php-fpm"]