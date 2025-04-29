
# Helpline System Deployment Guide (Localhost Setup)

This guide will help you successfully deploy the Helpline System (Frontend + Backend) on your localhost environment.

---

## Prerequisites

Ensure you have the following installed:

- **Ubuntu/Linux** system
- **Nginx** web server
- **PHP 8.1+** with FPM (`php-fpm`)
- **Composer** (for PHP dependency management)
- **MySQL/MariaDB** server
- **Git** (for cloning the repository)
- **Node.js** and **npm** (optional, if you plan to modify/build frontend assets)

---

## Step-by-Step Setup Instructions

### 1. Clone the repositories

Navigate to your web server directory:

```bash
cd /var/www/html
```

Clone the backend repository:

```bash
git clone https://github.com/openchlai/rest_api.git helpline
```

Clone the frontend repository:

```bash
git clone https://github.com/openchlai/application.git frontend
```

Ensure the structure looks like this:

```
/var/www/html/
  ├── helpline/
  │    ├── api/
  │    ├── config.php
  │    ├── lib/
  │    ├── tests/
  │    ├── vendor/
  │    └── uchl.sql
  ├── frontend/
  │    ├── app/
  │    ├── images/
  │    ├── js/
  │    ├── index.php
  │    └── screen.css
```

**Important:** Frontend and backend must both exist under `/var/www/html/`.

---

### 2. Set up Database

Create a database and import the SQL file:

```bash
mysql -u root -p
```

Then inside MySQL:

```sql
CREATE DATABASE helpline;
USE helpline;
SOURCE /var/www/html/helpline/uchl.sql;
EXIT;
```

Update your `/var/www/html/helpline/config.php` with correct DB credentials if needed.

---

### 3. Configure Nginx

Create a new Nginx config file:

```bash
sudo nano /etc/nginx/sites-available/helpline.conf
```

Paste the following configuration:

```nginx
server {
    listen 80;
    server_name localhost;

    root /var/www/html/frontend;
    index index.php index.html index.htm;

    location / {
        try_files $uri $uri/ /index.php?$args;
    }

    location ^~ /helpline/api/ {
        root /var/www/html;
        index index.php;
        try_files $uri /helpline/api/index.php?$args;
    }

    location /helpline/js/ {
        alias /var/www/html/frontend/js/;
        try_files $uri =404;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php8.4-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\. {
        deny all;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/helpline.conf /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

---

### 4. Setup PHP

Ensure `php-fpm` service is running:

```bash
sudo systemctl start php8.1-fpm
sudo systemctl enable php8.1-fpm
```

Check PHP modules:

```bash
php -m
```

Make sure at least these modules are installed:

- mysqli
- pdo_mysql
- curl
- mbstring
- json
- fileinfo

Install missing modules:

```bash
sudo apt install php-mysql php-curl php-mbstring php-json php-fileinfo
```

---

### 5. Permissions

Set permissions for your project folders:

```bash
sudo chown -R www-data:www-data /var/www/html/frontend
sudo chown -R www-data:www-data /var/www/html/helpline
sudo chmod -R 755 /var/www/html/
```

---

## Additional Notes

- **Frontend**: Access the UI via `http://localhost/`
- **Backend API**: Access API endpoints via `http://localhost/helpline/api/`
- **WebSocket errors**: Ignore WebSocket errors (`sip.js`) if you're not running a WebSocket server at `wss://localhost:8089/`
- **Quirks Mode Warning**: Add `<!DOCTYPE html>` at the top of your frontend `index.php` to fix.

Example:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Helpline System</title>
</head>
<body>
    <!-- your content -->
</body>
</html>
```

---

## Troubleshooting

| Problem | Solution |
|--------|----------|
| Files downloading instead of executing PHP | Ensure `php-fpm` is installed and Nginx is using `fastcgi_pass` correctly |
| Grey blank page | Check browser console for missing files or PHP errors |
| 500 Internal Server Error on API | Check `/var/log/nginx/error.log` and fix PHP code or database connection |

---

## Final Check

Visit:

- [http://localhost/](http://localhost/) — Frontend should load
- [http://localhost/helpline/api/](http://localhost/helpline/api/) — Backend API should respond

---

## Deployment Success!

🎉 You have successfully deployed the Helpline System on your localhost!

---

## Repositories

- **Backend**: [https://github.com/openchlai/rest_api.git](https://github.com/openchlai/rest_api.git)
- **Frontend**: [https://github.com/openchlai/application.git](https://github.com/openchlai/application.git)

---

