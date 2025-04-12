FROM r-base:4.3.1

# These will allow for the renv install
ENV RENV_VERSION 1.0.7
ENV RENV_PATHS_LIBRARY renv/library
ENV QUARTO_VERSION 1.4.555

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
RUN R -e "remotes::install_github('rstudio/renv@v${RENV_VERSION}')"

WORKDIR /data_guide
# only copy renv file
COPY renv.lock renv.lock

RUN R -e "renv::restore()"

# Must install quarto cli
WORKDIR /opt
# RUN wget "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.tar.gz"
RUN wget "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.tar.gz"
RUN tar -C /opt -xvzf quarto-${QUARTO_VERSION}-linux-amd64.tar.gz

# Set quarto path
ENV PATH="${PATH}:/opt/quarto-${QUARTO_VERSION}/bin/"

RUN quarto install tinytex

WORKDIR /data_guide
COPY . .
# have to run this command again for some reason
RUN R -e "renv::restore()"
