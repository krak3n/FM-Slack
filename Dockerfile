FROM debian:wheezy

RUN apt-get update && apt-get install -y \
        build-essential \
        python-dev \
        python-setuptools \
    && apt-get clean \
    && apt-get autoclean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/

WORKDIR /fm

EXPOSE 5000

ADD . /fm

# Install Application
RUN python setup.py install
