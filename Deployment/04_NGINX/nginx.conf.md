# For more information on configuration, see:
#   * Official English Documentation: [http://nginx.org/en/docs/](http://nginx.org/en/docs/)
#   * Official Russian Documentation: [http://nginx.org/ru/docs/](http://nginx.org/ru/docs/)

user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

# Load dynamic modules. See /usr/share/doc/nginx/README.dynamic.
include /usr/share/nginx/modules/*.conf; 

events {
    worker_connections 1024;
}

http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 4096;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    # Load modular configuration files from the /etc/nginx/conf.d directory.
    # See [http://nginx.org/en/docs/ngx_core_module.html#include](http://nginx.org/en/docs/ngx_core_module.html#include)
    # for more information.
    include /etc/nginx/conf.d/*.conf;

    server {
        listen       80 default_server;
#        listen       [::]:80 default_server;
        server_name  _;
        root         /var/www/html;

        # Load configuration files for the default server block.
        include /etc/nginx/default.d/*.conf;

        location / {
        }

        error_page 404 /404.html;
            location = /40x.html {
        }

        error_page 500 502 503 504 /50x.html;
            location = /50x.html {
        }
    }

# Settings for a TLS enabled server.
# openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/pki/nginx/private/server.key -out /etc/pki/nginx/server.crt
    server {
        listen       443 ssl http2 default_server;
#        listen       [::]:443 ssl http2 default_server;
        server_name  _;
        root         /var/www/html;

        ssl_certificate "/etc/pki/voiceapps/voiceapps.crt";
        ssl_certificate_key "/etc/pki/voiceapps/private/voiceapps.key";
        ssl_session_cache shared:SSL:1m;
        ssl_session_timeout  10m;
        ssl_ciphers PROFILE=SYSTEM;
        ssl_prefer_server_ciphers on;

        # Load configuration files for the default server block.
        include /etc/nginx/default.d/*.conf;

        location / {
        }

        error_page 404 /404.html;
            location = /40x.html {
        }

        error_page 500 502 503 504 /50x.html;
            location = /50x.html {
        }

        
	location /tower/{
                index index.php index.html index.htm;
                try_files $uri $uri/ /tower/api/index.php?$args;
        }

	location /wallboard/{
                
                 
        }

    }

    server {
        listen     8384 ssl;
        ssl_certificate "/etc/pki/voiceapps/voiceapps.crt";
        ssl_certificate_key "/etc/pki/voiceapps/private/voiceapps.key";
	location / {
		proxy_read_timeout 		300s;
        	proxy_http_version 		1.1;
                proxy_set_header Host           $host;
		proxy_set_header Connection 	$http_connection; #"Upgrade";
                proxy_set_header Upgrade        $http_upgrade;
                proxy_set_header XCLIENTIP      $remote_addr;
		proxy_pass                      http://127.0.0.1:8383/;
	}
    }
}
