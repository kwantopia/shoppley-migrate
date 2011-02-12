server {
    listen 80;
    server_name media.shoppley.com;

    location / {
        root /home/www/shoppley.com/shoppley/;
        index index.html;
    }
}
