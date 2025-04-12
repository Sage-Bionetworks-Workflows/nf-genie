FROM python:3.11

ENV QUARTO_VERSION 1.6.42

# Must install quarto cli
WORKDIR /opt
RUN wget "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.tar.gz"
RUN tar -C /opt -xvzf quarto-${QUARTO_VERSION}-linux-amd64.tar.gz

# Set quarto path
ENV PATH="${PATH}:/opt/quarto-${QUARTO_VERSION}/bin/"

RUN quarto install tinytex

WORKDIR /data_guide
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
