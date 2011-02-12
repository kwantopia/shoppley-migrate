server {
    listen 80; 
    server_name www.m.shoppley.com;
    rewrite ^/(.*) http://m.shoppley.com/$1 permanent;
}

server {
    listen 80;
    server_name m.shoppley.com;

    access_log /home/www/shoppley.com/nginx/logs/access.log;
    error_log /home/www/shoppley.com/nginx/logs/error.log;

    location / {
        #root /home/www/shoppley.com/htdocs/;
        #index index.html;
        proxy_pass http://127.0.0.1:8089/m/;
        include /etc/nginx/proxy.conf;
    }

}
