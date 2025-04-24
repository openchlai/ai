<<<<<<< HEAD
1. **Connect to the CentOS 9 server:**
   - Launch the VMware application.
   - Power on the CentOS 9 virtual machine.
   - Wait for the CentOS login prompt.
   - Log in to the CentOS 9 server using your credentials.

2. **Install Nginx:**
   - Run the following command to install Nginx Mysql and php:
     ```
     yum install mariadb-server mariadb-devel nginx php php-mysqlnd php-fpm
     ```

3. **Start and enable Nginx service:**
   - Run the following command to start the Nginx service:
     ```
     sudo systemctl start nginx
     ```
   - Run the following command to enable the Nginx service to start on system boot:
     ```
     sudo systemctl enable nginx
     ```

4. **Configure Nginx: **
   - Copy the Nginx the  provided configuration file for nginx:


     ```
     cp /usr/src/Sacco_CRM/src/nginx.conf /etc/nginx/.
    
     ```

      ```
     cp /usr/src/Sacco_CRM/src/www.conf /etc/php-fpm.d/.
    
     ```

     ```
     cp  /usr/src/Sacco_CRM/src/tower_config.php /var/www/.
    ```

     ```
      sudo cp -r /usr/src/Sacco_CRM/src/tower /var/www/html/.
     ```

     
  
   - To view the content of the configuration file us the following:


     [Default Nginx Configuration](../../src/nginx.conf)


   - Save and close the file.
   - Generate SSL Certificate 

    ```mkdir -p /etc/pki/voiceapps/private```
  
      ```openssl req -x509 -nodes -days 365 -newkey rsa:4096 -keyout /etc/pki/voiceapps/private/voiceapps.key -out /etc/pki/voiceapps/voiceapps.crt
      ```

5. Disable SE Linus 
   ```sudo getenforce```

   ```setenforce 0```



6. **Restart Nginx and PHP-FPM:**
   - Run the following commands to restart the Nginx and PHP-FPM services:
     ```
     sudo systemctl restart nginx
     sudo systemctl restart php-fpm
     ```

7. **configure the firewall**

    ```sudo firewall-cmd --permanent --add-port=443/tcp```

    ```sudo firewall-cmd --permanent --add-port=8384/tcp```

8. **Test the Nginx and PHP setup:**
   - Create a PHP test file by running the following command:
     ```
     echo "<?php phpinfo(); ?>" | sudo tee /usr/share/nginx/html/phpinfo.php
     ```
   - Open a web browser on your local machine and enter the following URL:
     ```
     http://<server-ip-address>/phpinfo.php
     ```
     Replace `<server-ip-address>` with the actual IP address of your CentOS 9 server.
   - If everything is set up correctly, you should see the PHP information page.
 - 
=======
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
>>>>>>> d1d56571d16d5f5602786158425245af41cfa963
