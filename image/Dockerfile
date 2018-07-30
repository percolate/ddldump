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


ENV PYTHON_PIP_VERSION="18.0" \
    DDLDUMP_VERSION="0.3"


RUN set -eux; \
    python3 -m ensurepip; \
    pip3 install "pip==${PYTHON_PIP_VERSION}"; \
    pip3 install -U "ddldump==${DDLDUMP_VERSION}"

##
## Switch back to inherited settings
##

USER circleci
WORKDIR /home/circleci
