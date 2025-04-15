
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