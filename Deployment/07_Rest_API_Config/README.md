# Deployment Guide for VanillaJS + PHP Application on Ubuntu Server

## Server Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git curl unzip
```

## Install PHP and Required Extensions

```bash
# Add PHP repository
sudo add-apt-repository ppa:ondrej/php -y
sudo apt update

# Install PHP 8.3 and extensions
sudo apt install -y php8.3 php8.3-fpm php8.3-mysql php8.3-curl php8.3-gd php8.3-mbstring php8.3-xml php8.3-zip

# Verify PHP installation
php -v
```

## Install and Configure Nginx

```bash
# Install Nginx
sudo apt install -y nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

## Clone Your Repository

```bash
# Create project directory
sudo mkdir -p /var/www/helpline
sudo chown -R $USER:$USER /var/www/helpline

# Clone your repository
cd /var/www/helpline
git clone https://github.com/openchlai/ai/ .
```

## Nginx Configuration

Create `/etc/nginx/sites-available/helpline` with the following content:

```nginx
server {
    listen 80;
    server_name 154.72.207.59;

    root /var/www/helpline/frontend/;
    index index.html;

    location /helpline/ {
        alias /var/www/helpline/frontend/;
        try_files $uri $uri/ /helpline/index.html;
    }

    location /helpline/api/ {
        root /var/www/helpline/backend/;
        index index.php;

        add_header X-Frame-Options "SAMEORIGIN";
        add_header X-Content-Type-Options "nosniff";

        location ~ \.php$ {
            include snippets/fastcgi-php.conf;
            fastcgi_pass unix:/run/php/php8.3-fpm.sock;
            fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
            include fastcgi_params;
        }

        try_files $uri $uri/ /helpline/api/index.php$is_args$args;
    }

    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location ~ /\. {
        deny all;
    }

    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 365d;
    }
}
```

Enable the configuration:

```bash
sudo ln -s /etc/nginx/sites-available/helpline /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## PHP-FPM Configuration

Edit `/etc/php/8.3/fpm/php.ini` and update the following:

```ini
upload_max_filesize = 20M  
post_max_size = 20M  
memory_limit = 256M  
max_execution_time = 300  
```

Restart PHP-FPM:

```bash
sudo systemctl restart php8.3-fpm
```

## Set Proper Permissions

```bash
sudo chown -R www-data:www-data /var/www/helpline
sudo find /var/www/helpline -type d -exec chmod 755 {} \;
sudo find /var/www/helpline -type f -exec chmod 644 {} \;
```

## Install Composer (if needed)

```bash
curl -sS https://getcomposer.org/installer | sudo php -- --install-dir=/usr/local/bin --filename=composer
cd /var/www/helpline/backend
composer install
```

## Server Security

```bash
# Configure firewall
sudo apt install -y ufw
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable

# SSL with Let's Encrypt (optional)
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Testing

Frontend: http://154.72.207.59/helpline/

API: http://154.72.207.59/helpline/api/

## Troubleshooting

```bash
# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# PHP-FPM logs
sudo tail -f /var/log/php8.3-fpm.log

# Service status
sudo systemctl status php8.3-fpm
```
