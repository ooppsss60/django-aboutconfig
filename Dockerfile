FROM fkrull/multi-python

ENV WORKDIR=/code

WORKDIR $WORKDIR

ADD . $WORKDIR

RUN apt update -y && apt install -y curl && apt clean
RUN pip3 install -r $WORKDIR/requirements/dj22.txt

CMD $WORKDIR/scripts/docker_start.sh
