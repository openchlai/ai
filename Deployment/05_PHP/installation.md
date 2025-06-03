<<<<<<< HEAD
1. **Connect to the CentOS 9 server:**
   - Launch the VMware application.
   - Power on the CentOS 9 virtual machine.
   - Wait for the CentOS login prompt.
   - Log in to the CentOS 9 server using your credentials.

2. **Update the system:**
   - Run the following command to update the system packages:
     ```
     sudo yum update
     ```

3. **Install PHP and related packages:**
   - Run the following command to install PHP and commonly used PHP modules:
     ```
     sudo yum install php php-cli php-fpm php-mysqlnd php-json php-opcache php-xml php-gd php-curl php-mbstring
     ```

     ```
     sudo chown -R nginx:nginx /var/log/php-fpm
     ```
     

4. **Start and enable PHP-FPM service:**
   - Run the following command to start the PHP-FPM service:
     ```
     sudo systemctl start php-fpm
     ```
   - Run the following command to enable the PHP-FPM service to start on system boot:
     ```
     sudo systemctl enable php-fpm
     ```

5. **Verify the PHP installation:**
   - Create a PHP test file by running the following command:
     ```
     echo "<?php phpinfo(); ?>" | sudo tee /var/www/html/phpinfo.php
     ```
   - Open a web browser on your local machine and enter the following URL:
     ```
     http://<server-ip-address>/phpinfo.php
     ```
     Replace `<server-ip-address>` with the actual IP address of your CentOS 9 server.
   - If PHP is installed correctly, you should see the PHP information page with details about your PHP installation.
=======

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
>>>>>>> d1d56571d16d5f5602786158425245af41cfa963
