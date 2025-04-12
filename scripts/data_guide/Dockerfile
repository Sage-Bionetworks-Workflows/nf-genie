FROM python:3.11

ENV QUARTO_VERSION 1.6.42

# RUN apt-get update && apt-get -y install \
#       libpng-dev \
#       python3 \
#       python3-dev \
#       python3-pip \
#       python3-venv \
#       curl \
#       # procps is required for nextflow tower
#       procps \
#       # libtex dependencies
#       cmake \
#       libfontconfig1-dev \
#       libharfbuzz-dev \
#       libfribidi-dev \
#       libssl-dev \
#       libcairo2-dev \
#       libfreetype6-dev libpng-dev libtiff5-dev libjpeg-dev libxml2-dev\
#       libcurl4-openssl-dev && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# Must install quarto cli
WORKDIR /opt
RUN wget "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.tar.gz"
RUN tar -C /opt -xvzf quarto-${QUARTO_VERSION}-linux-amd64.tar.gz

# Set quarto path
ENV PATH="${PATH}:/opt/quarto-${QUARTO_VERSION}/bin/"

RUN quarto install tinytex

COPY . .
RUN pip install -r requirements.txt
