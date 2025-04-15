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
