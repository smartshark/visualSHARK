FROM ubuntu:16.04


# Install dependencies
RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update
RUN apt-get install -y build-essential wget git
RUN apt-get install -y python3.6
RUN apt-get install -y python3.6-dev
RUN apt-get install -y python3.6-venv
RUN apt-get install -y uwsgi uwsgi-src uuid-dev libcap-dev libpcre3-dev libssl-dev
RUN apt-get install -y graphviz-dev
RUN apt-get install -y rabbitmq-server
RUN apt-get install -y libmysqlclient-dev
RUN apt-get install -y python3-pip python3-cffi
RUN apt-get install -y rabbitmq-server
RUN apt-get install -y curl

# Python3.6 wsgi module
RUN PYTHON=python3.6 uwsgi --build-plugin "/usr/src/uwsgi/plugins/python python36"
RUN mv python36_plugin.so /usr/lib/uwsgi/plugins/python36_plugin.so
RUN chmod 644 /usr/lib/uwsgi/plugins/python36_plugin.so

# Add NPM
RUN curl -sL https://deb.nodesource.com/setup_6.x -o nodesource_setup.sh
RUN bash nodesource_setup.sh
RUN apt-get install -y nodejs

# Add rabbitmq-server
# TODO

# Install Backend
RUN apt-get install libmysqlclient-dev
RUN git clone --recursive https://github.com/smartshark/visualSHARK /root/visualshark
RUN python3.6 -m pip install -r /root/visualshark/requirements.txt
RUN python3.6 -m pip install pygraphviz --install-option="--include-path=/usr/include/graphviz" --install-option="--library-path=/usr/lib/graphviz/"
RUN cp /root/visualshark/sntest/settings_dist.py /root/visualshark/sntest/settings.py
# Change settings
# Migrate Database
# Create superuser

# Install Frontend
RUN npm install /root/visualshark/frontend/app
RUN cp /root/visualshark/frontend/app/config/prod.local.env.js /root/visualshark/frontend/app/config/prod.env.js