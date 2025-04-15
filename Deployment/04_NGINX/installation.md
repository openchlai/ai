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