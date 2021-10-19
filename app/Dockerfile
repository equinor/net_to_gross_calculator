# Dockerfile for the Geo:N:G web application. Build it from the /Geo_N_G folder using:
#
#     $ docker build -t geong_app -f app/Dockerfile .
#
# You can then run it as a container:
#
#     $ docker run --rm -p 8080:8080 geong_app

FROM python:3.8.12-slim-buster

# Install Python dependencies with pip
COPY ./app/requirements.txt ./app/
RUN python -m pip install -r ./app/requirements.txt \
    --no-cache-dir --disable-pip-version-check

# Create working directory
WORKDIR /src

# Install geong_common
COPY ./geong_common/geong_common ./geong_common/geong_common
COPY ./geong_common/MANIFEST.in ./geong_common/setup.py ./geong_common/setup.cfg \
    ./geong_common/pyproject.toml ./geong_common/
RUN python -m pip install ./geong_common --no-cache-dir --disable-pip-version-check

# Install app
COPY ./app/app ./app/app
COPY ./app/MANIFEST.in ./app/setup.py ./app/setup.cfg ./app/pyproject.toml ./app/
RUN python -m pip install ./app --no-cache-dir --disable-pip-version-check

# Don't run as root
USER 2000:2000

LABEL org.opencontainers.image.source https://github.com/equinor/geong

# Serve the Geo:N:G app when the container is run
EXPOSE 8080
CMD ["panel", "serve", "--port=8080", "./app/app", "--static-dirs", "images=./app/app/assets/images"]
