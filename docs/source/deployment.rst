Deployment
==========


nginx
-----

Nginx terminates HTTP / HTTPS, serves static content.

nginx backend configuration example::

    server {
        listen *:443 ssl;
        #server_name vsbackend.domain.tld;

        access_log /var/log/nginx/vsbackend.access_log main;
        error_log /var/log/nginx/vsbackend.error_log info;

        ssl_verify_depth 3;
        ssl_certificate /etc/ssl/nginx/chain.pem;
        ssl_certificate_key /etc/ssl/nginx/server.key;

        location / {
            include uwsgi_params;
            uwsgi_pass unix:/run/uwsgi/app/visualshark/socket;
        }

        location /static {
            alias /srv/www/visualSHARK/static/;
        }
    }
    server {
        listen *:80;
        server_name vsbackend.domain.tld;

        location '/.well-known/acme-challenge' {
            default_type "text/plain";
            root /tmp/challenges/;
        }

        location / {
            return 301 https://vsbackend.domain.tld$request_uri;
        }
    }

nginx frontend configuration example::

    server {
        listen *:443 ssl;
        server_name visualshark.domain.tld;

        access_log /var/log/nginx/visualshark.access_log main;
        error_log /var/log/nginx/visualshark.error_log info;

        ssl_verify_depth 3;
        ssl_certificate /etc/ssl/nginx/chain.pem;
        ssl_certificate_key /etc/ssl/nginx/server.key;

        root /srv/www/visualSHARK/frontend/app/dist/;
    }

    server {
        listen *:80;
        server_name visualshark.domain.tld;

        location '/.well-known/acme-challenge' {
            default_type "text/plain";
            root /tmp/challenges/;
        }

        location / {
            return 301 https://visualshark.domain.tld$request_uri;
        }
    }


uwsgi
-----

Runs the django backend.

uwsgi configuration example::

    [uwsgi]
    chdir = /srv/www/visualSHARK/
    threads = 1
    module = sntest.wsgi:application
    vacuum = True
    master = True
    plugins = python36
    virtualenv = /srv/www/visualSHARK/
    uid = www-data
    gid = www-data
    env = DJANGO_SETTINGS_MODULE=sntest.settings


Systemd worker
--------------

Systemd runs a the worker process.

systemd worker example::

    [Unit]
    Description=VisualSHARK Worker

    [Service]
    Type=simple
    ExecStart=/srv/www/visualSHARK/bin/python /srv/www/visualSHARK/manage.py peon

    [Install]
    WantedBy=multi-user.target

