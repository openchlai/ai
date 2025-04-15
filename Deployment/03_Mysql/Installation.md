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

7. create the sql user account.

    ```sudo mysql```

    * then on the mysql command you can create a user
    ```create user nginx@localhost identified via unix_socket;```

    ```create database tower;```

    ```use tower;```

    ```exit```

   ```mysql tower < /usr/src/Sacco_CRM/src/tower_schema.sql```

- Grant Authorization to the Nginx User 

    ```grant select,insert on tower.* to nginx@localhost;```

    ```grant update on tower.auth to nginx@localhost;```

    ```grant update on tower.contact to nginx@localhost;```

    ```grant update on tower.kase to nginx@localhost;```

    ```grant update on tower.kase_activity to nginx@localhost;```

    ```grant update on tower.activity to nginx@localhost;```
    
    ```grant update on tower.disposition to nginx@localhost;```

    ```grant delete on tower.session to nginx@localhost;```

    ```grant update on tower.chan to nginx@localhost;```
