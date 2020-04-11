FROM fkrull/multi-python

ENV WORKDIR=/code \
    DB_PATH=/db/django.db

WORKDIR $WORKDIR

ADD . $WORKDIR

VOLUME /db
# make image smaller
RUN apt update \
    apt install -y curl \
    rm -rf /var/lib/apt/lists/* \
    && apt purge -y python2.3* python2.4* python2.5* python2.6* python3.1* python3.2* python3.3* python3.4* python3.5* \
    && apt autoremove --purge -y
RUN pip3 install -r $WORKDIR/requirements/dj30.txt python-memcached

CMD $WORKDIR/scripts/docker_start.sh
