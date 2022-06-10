# Dockerfile for the Geo:N:G web application. Build it from the /Geo_N_G folder using:
#
#     $ docker build -t geong_app -f app/Dockerfile .
#
# You can then run it as a container:
#
#     $ docker run --rm -p 8080:8080 geong_app
FROM python:3.10.5-slim-buster

ENV HOME /home/u
RUN mkdir -p $HOME
RUN chown 2000:2000 $HOME
USER 2000:2000
WORKDIR $HOME
ENV PATH $PATH:$HOME/.local/bin

# Install Python dependencies with pip
RUN mkdir app
COPY ./app/requirements.txt ./app/
RUN python -m pip install -r ./app/requirements.txt\
 --no-cache-dir --disable-pip-version-check

# Install geong_common
RUN mkdir geong_common
COPY ./geong_common/geong_common ./geong_common/geong_common
COPY ./geong_common/MANIFEST.in ./geong_common/setup.py\
 ./geong_common/setup.cfg ./geong_common/pyproject.toml ./geong_common/
RUN python -m pip install ./geong_common --no-cache-dir --disable-pip-version-check\
 --use-feature=in-tree-build

# Install app
COPY ./app/app ./app/app
COPY ./app/MANIFEST.in ./app/setup.py ./app/setup.cfg ./app/pyproject.toml ./app/
RUN python -m pip install ./app --no-cache-dir --disable-pip-version-check\
 --use-feature=in-tree-build

LABEL org.opencontainers.image.source https://github.com/equinor/geong

# Serve the Geo:N:G app when the container is run
EXPOSE 8080
CMD ["panel", "serve", "--port=8080", "./app/app", "--static-dirs", "images=./app/app/assets/images"]
