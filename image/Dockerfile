FROM circleci/python

##
## Switch to root so installations can proceed
##

USER root

ENV POSTGRES="postgresql-client-9.6" \
    MYSQL="mysql-client"

RUN apt-get update; \
    apt-get install -y --no-install-recommends ${POSTGRES} ${MYSQL}; \
    apt-get purge -y; \
    rm -rf /var/lib/apt/lists/*


COPY ddldump /ddldump
COPY setup.* /


RUN set -eux; \
    python setup.py bdist_wheel; \
    python3 -m ensurepip; \
    pip3 install -U /dist/*

ENTRYPOINT ["ddldump"]
