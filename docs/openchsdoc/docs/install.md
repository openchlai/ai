# Installation

- **Centos:** Follow the installation guide for CentOS by [linking to the CentOS installation readme](https://github.com/openchlsystem/OpenCHS-helpline/blob/main/03_Deployment/01_Centos/README.md).

- **Nginx:** Install Nginx by referring to the [Nginx installation readme](https://github.com/openchlsystem/OpenCHS-helpline/blob/main/03_Deployment/04_NGINX/README.md).

- **PHP:** Set up PHP by following the instructions in the [PHP installation readme](https://github.com/openchlsystem/OpenCHS-helpline/blob/main/03_Deployment/05_PHP/README.md).

- **JavaScript:** No specific installation steps are required for JavaScript as it is a client-side language.

- **Asterisk:** Install and configure Asterisk by referring to the [Asterisk installation readme](https://github.com/openchlsystem/OpenCHS-helpline/blob/main/03_Deployment/06_ASTERISK/README.md).

- **MySQL:** Set up MySQL by following the instructions in the [MySQL installation readme](https://github.com/openchlsystem/OpenCHS-helpline/blob/main/03_Deployment/03_Mysql/README.md).

Once all the necessary components are installed, you can proceed with the application setup:

- Clone the application repository from

    - Step 1: Clone the repository ```  git clone <repository_url> ```

    - Step 2: Enable sparse checkout  ```  cd <repository_directory> ```

        ```  git sparse-checkout init ```

    - Step 3: Specify the "src" folder to include ```  git sparse-checkout set src ```

    - Step 4: Update your working directory ```  git pull ```

- Configure the Nginx server to point to the application's root directory.
- Import the MySQL database schema provided in the repository.
- Update the necessary configuration files (if any) to reflect your environment settings.
- Start the Asterisk server and configure it to work with the application.
- Launch the application by running the appropriate commands or accessing it through the Nginx server.

Additional instructions or dependencies specific to your application may be mentioned in the repository's README or installation guide. Be sure to refer to those for a complete and accurate installation process.

For any further assistance or troubleshooting, please refer to the Support section or contact the project maintainers listed in the Authors section.