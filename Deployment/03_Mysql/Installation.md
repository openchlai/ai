Installation Steps:

1. Update the System:
    * Connect to your CentOS server using SSH or open a terminal.
    * Update the package lists by running the following command:

    ```bash
    sudo yum update
    ```

2. Install MariaDB Server:
    * Run the following command to install MariaDB Server:

    ```bash
    sudo yum install mariadb-server
    ```

3. Start the MariaDB Service:
    * After the installation is complete, start the MariaDB service using the following command:

    ```bash
    sudo systemctl start mariadb
    ```

4. Enable MariaDB to start on system boot:
    * Run the following command to enable MariaDB to start automatically on system boot:

    ```bash
    sudo systemctl enable mariadb
    ```

5. Secure the MariaDB Installation:
    * Run the secure installation script that comes with MariaDB Server by executing the following command:

    ```bash
    sudo mysql_secure_installation
    ```

    * You will be prompted to enter the root password. If this is the first time you are running the script, there may not be a password set. Press Enter to proceed.
    * Follow the prompts to set a root password, remove anonymous users, disallow root login remotely, remove the test database, and reload the privilege tables.

6. Verify the Installation:
    * Check the status of the MariaDB service to ensure it is running properly by running the following command:

    ```bash
    sudo systemctl status mariadb
    ```

    * You should see an "active (running)" message if MariaDB is running correctly.

7. ## 1. Database Setup

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