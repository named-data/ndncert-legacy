FROM ubuntu:16.04

MAINTAINER aa@cs.fiu.edu

RUN rm -rf /etc/apt/apt.conf.d/docker-gzip-indexes \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-setuptools python3-dev build-essential git libssl-dev libffi-dev libsqlite3-dev libboost-all-dev \
 && rm -rf /var/lib/apt/lists/*

RUN easy_install3 pip \
 && pip3 install requests

RUN git clone https://github.com/named-data/PyNDN2 \
 && cd PyNDN2 \
 && python3 setup.py install \
 && cd ../ && rm -Rf PyNDN2

RUN git clone https://github.com/named-data/ndn-cxx \
 && cd ndn-cxx \
 && ./waf configure build install \
 && cd ../ && rm -Rf ndn-cxx

RUN ldconfig

COPY ndnop-process-requests /usr/bin/ndnop-process-requests

# docker build -t ndnop:latest .
