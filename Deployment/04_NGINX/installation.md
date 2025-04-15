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
