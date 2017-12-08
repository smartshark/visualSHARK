About
=====
The visualSHARK is a graphical frontend for the MongoDB of the SmartSHARK project.


Requirements
============

Requirements and how to get them with Ubuntu 16.04 LTS.

Python 3.6
----------
add-apt-repository ppa:jonathonf/python-3.6
apt-get update
apt-get install python3.6
apt-get install python3.6-dev
apt-get install python3.6-venv

python-3.6 uwsgi
----------------
apt-get install python3.6 python3.6-dev uwsgi uwsgi-src uuid-dev libcap-dev libpcre3-dev
cd ~
PYTHON=python3.6 uwsgi --build-plugin "/usr/src/uwsgi/plugins/python python36"
mv python36_plugin.so /usr/lib/uwsgi/plugins/python36_plugin.so
chmod 644 /usr/lib/uwsgi/plugins/python36_plugin.so

pygraphviz
----------
pip install pygraphviz --install-option="--include-path=/usr/include/graphviz" --install-option="--library-path=/usr/lib/graphviz/"


NPM
---

In Xenial ist nur Node4, hier mit PPA Node 6
cd ~
curl -sL https://deb.nodesource.com/setup_6.x -o nodesource_setup.sh
nano nodesource_setup.sh
bash nodesource_setup.sh
apt-get install nodejs


RabbitMQ Install
----------------
apt-get install rabbitmq-server
rabbitctl enable web_stomp, management
