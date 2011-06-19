# TODO: Remove this when all switched to logging.
WSGIRestrictStdout Off

<VirtualHost 127.0.0.1:8089>
    ServerName www.shoppley.com
    ServerAlias shoppley.com
    ServerAdmin webmaster@shoppley.com

    #<Directory /home/www/shoppley.com/shoppley/static>
    #	Order deny,allow
    #	Allow from all
    #</Directory>

	WSGIDaemonProcess shoppley.com processes=2 threads=15 display-name=${GROUP} python-path=/home/virtual/shoppley-env/lib/python2.7/site-packages
	WSGIProcessGroup shoppley.com

	#WSGIScriptAlias / /home/www/shoppley.com/shoppley/apache/shoppley.wsgi
	WSGIScriptAlias / /home/www/shoppley.com/shoppley/deploy/pinax.wsgi

	<Directory /home/www/shoppley.com/shoppley/deploy>
		Order allow,deny
		Allow from all
	</Directory>

	ErrorLog /home/www/shoppley.com/logs/error.log	
	# Possible values include: debug, info, notice, warn, error, crit,
	# alert, emerg.
	LogLevel warn

	CustomLog /home/www/shoppley.com/logs/access.log combined

</VirtualHost>
