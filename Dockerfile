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

# Clone repository
RUN git clone --recursive https://github.com/smartshark/visualSHARK /root/visualshark
