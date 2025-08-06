C
C
C
# REST API Setup Documentation

## 1. Database Setup

### 1.1 Create User
Run the following command to create a MySQL user with `unix_socket` authentication:
```bash
sudo mysql -e "CREATE USER 'nginx'@'localhost' IDENTIFIED VIA unix_socket;"
```

### 1.2 Create Database
Create the database `helpline`:
```bash
sudo mysql -e "CREATE DATABASE helpline;"
```

### 1.3 Import Database Schema
Import the database schema into the `helpline` database:
```bash
sudo mysql helpline < /usr/src/OpenChs/rest_api/uchl.sql
```

### 1.4 Grant Permissions
Grant necessary permissions to the `nginx` user:
```bash
sudo mysql -e "
GRANT SELECT, INSERT ON helpline.* TO 'nginx'@'localhost';
GRANT UPDATE ON helpline.auth TO 'nginx'@'localhost';
GRANT UPDATE ON helpline.contact TO 'nginx'@'localhost';
GRANT UPDATE ON helpline.kase TO 'nginx'@'localhost';
GRANT UPDATE ON helpline.kase_activity TO 'nginx'@'localhost';
GRANT UPDATE ON helpline.activity TO 'nginx'@'localhost';
GRANT UPDATE ON helpline.disposition TO 'nginx'@'localhost';
GRANT DELETE ON helpline.session TO 'nginx'@'localhost';
GRANT UPDATE ON helpline.chan TO 'nginx'@'localhost';
FLUSH PRIVILEGES;"
```

### 1.5 Exit MySQL
Exit the MySQL prompt:
```bash
exit
```

---

## 2. Server Setup

### 2.1 Install Nginx
Install Nginx:
```bash
sudo apt-get install nginx
```

### 2.2 Configure Nginx
Edit the Nginx configuration file (`/etc/nginx/nginx.conf`) and add the following server blocks:

#### Server Block for API and Web Application
```nginx
server {
    listen 443 ssl;
    server_name _;
    root /var/www/html;

    ssl_certificate "/etc/pki/openchs/openchs.crt";
    ssl_certificate_key "/etc/pki/openchs/private/openchs.key";
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';

    location / {
    }

    error_page 404 /404.html;
    location = /40x.html {}

    error_page 500 502 503 504 /50x.html;
    location = /50x.html {}

    location /helpline/ {
        index index.php index.html index.htm;
        try_files $uri $uri/ /helpline/api/index.php?$args;
    }

    location / {
        proxy_read_timeout 300s;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header Connection $http_connection;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header XCLIENTIP $remote_addr;
        proxy_pass http://127.0.0.1:8383/;
    }
}
```

---

## 3. PHP-FPM Configuration

### 3.1 Create PHP-FPM Upstream
Create the `/etc/nginx/conf.d/php-fpm.conf` file:
```nginx
upstream php-fpm {
    server unix:/run/php/php8.2-fpm.sock;
}
```

### 3.2 Create PHP Configuration
Create the `/etc/nginx/default.d/php.conf` file:
```nginx
index index.php index.html index.htm;

location ~ \.(php|phar)(/.*)?$ {
    fastcgi_split_path_info ^(.+\.(?:php|phar))(/.*)$;
    fastcgi_intercept_errors on;
    fastcgi_index index.php;
    include fastcgi_params;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    fastcgi_param PATH_INFO $fastcgi_path_info;
    fastcgi_pass php-fpm;
}
```

---

## 4. REST API Setup

### 4.1 Install PHP
Install PHP:
```bash
sudo apt-get install php
```

### 4.2 Install PHP-MySQL
Install the PHP-MySQL extension:
```bash
sudo apt-get install php-mysql
```

### 4.3 Install PHP-FPM
Install PHP-FPM:
```bash
sudo apt-get install php-fpm
```

### 4.4 Configure PHP-FPM
Edit `/etc/php/8.2/fpm/php-fpm.conf`:
```ini
error_log = /var/log/php8.2-fpm.log
```

Edit `/etc/php/8.2/fpm/pool.d/www.conf`:
```ini
php_admin_value[error_log] = /var/log/fpm-php.www.log
php_admin_flag[log_errors] = on
listen = /run/php/php8.2-fpm.sock
listen.owner = nginx
listen.group = nginx
user = nginx
group = nginx
```

---

## 5. UI Setup

### 5.1 Copy Application Files
Copy application files to the web directory:
```bash
cp -r /home/<app_files_directory>/* /var/www/html/helpline/
```

---

This documentation provides step-by-step instructions for setting up the REST API, database, server, and application files.


