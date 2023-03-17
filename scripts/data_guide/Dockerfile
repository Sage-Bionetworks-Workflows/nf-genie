FROM r-base:4.2.2

ENV RENV_VERSION 0.16.0
ENV RENV_PATHS_LIBRARY renv/library

RUN apt-get update && apt-get -y install \
      libpng-dev \
      python3 \
      python3-dev \
      python3-pip \
      python3-venv \
      curl \
      # procps is required for nextflow tower
      procps \
      # libtex dependencies
      cmake \
      libfontconfig1-dev \
      libharfbuzz-dev \
      libfribidi-dev \
      libssl-dev \
      libcairo2-dev \
      libfreetype6-dev libpng-dev libtiff5-dev libjpeg-dev libxml2-dev\
      libcurl4-openssl-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN R -e "install.packages('remotes', repos = c(CRAN = 'https://cloud.r-project.org'))"
RUN R -e "remotes::install_github('rstudio/renv@${RENV_VERSION}')"

WORKDIR /data_guide
COPY renv.lock renv.lock

RUN R -e "renv::restore()"

COPY . .
