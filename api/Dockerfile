# Dockerfile for the Geo:N:G api. Build it from the /Geo_N_G folder using:
#
#     $ docker build -t geong_api -f api/Dockerfile .
#
# You can then run it as a container:
#
#     $ docker run --rm -p 5000:5000 geong_api
FROM python:3.10.4-slim-buster

ENV HOME /home/u
RUN mkdir -p $HOME
RUN chown 2000:2000 $HOME
USER 2000:2000
WORKDIR $HOME
ENV PATH $PATH:$HOME/.local/bin

# Install Python dependencies with pip
RUN mkdir api
COPY ./api/requirements.txt ./api/
RUN python -m pip install -r ./api/requirements.txt\
 --no-cache-dir --disable-pip-version-check

# Install geong_common
RUN mkdir geong_common
COPY ./geong_common/geong_common ./geong_common/geong_common
COPY ./geong_common/MANIFEST.in ./geong_common/setup.py ./geong_common/setup.cfg\
 ./geong_common/pyproject.toml ./geong_common/
RUN python -m pip install ./geong_common/ --no-cache-dir\
 --disable-pip-version-check

# Install api
COPY ./api/MANIFEST.in ./api/setup.py ./api/setup.cfg ./api/pyproject.toml ./api/
COPY ./api/api ./api/api
RUN python -m pip install ./api --no-cache-dir --disable-pip-version-check

LABEL org.opencontainers.image.source https://github.com/equinor/geong

EXPOSE 5000
CMD ["geong_api"]
