server {
	listen 80;
	server_name pgadmin.shoppley.com;

    location / {
        root /usr/share/phppgadmin/;
        index index.php;
    }

	location ~ .php$ {
		fastcgi_pass   127.0.0.1:9000; #this must point to the socket spawn_fcgi is running on.
		fastcgi_index  index.php;
		fastcgi_param  SCRIPT_FILENAME    /usr/share/phppgadmin/$fastcgi_script_name;  # same path as above
		include /etc/nginx/fastcgi_params;
	}
}
