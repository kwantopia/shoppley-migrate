server {
    listen 80; 
    server_name www.shoppley.com;
    rewrite ^/(.*) http://shoppley.com/$1 permanent;
}

server {
    listen 80;
    server_name shoppley.com;

    access_log /home/www/shoppley.com/nginx/logs/access.log;
    error_log /home/www/shoppley.com/nginx/logs/error.log;

    location /phppgadmin {
        root /usr/share/phppgadmin/;
        index index.php;
    }

    location / {
        #root /home/www/shoppley.com/htdocs/;
        #index index.html;
        proxy_pass http://127.0.0.1:8089/;
        include /etc/nginx/proxy.conf;
    }

}
