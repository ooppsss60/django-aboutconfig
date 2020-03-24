FROM fkrull/multi-python

ENV WORKDIR=/code \
    DB_PATH=/db/django.db

WORKDIR $WORKDIR

ADD . $WORKDIR

VOLUME /db
RUN rm -rf /var/lib/apt/lists/*
RUN pip3 install -r $WORKDIR/requirements/dj30.txt python-memcached

CMD $WORKDIR/scripts/docker_start.sh
