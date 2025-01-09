FROM ghcr.io/sage-bionetworks/synapsepythonclient:v4.6.1

WORKDIR /tmb

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN wget https://raw.githubusercontent.com/cBioPortal/datahub-study-curation-tools/refs/heads/master/tmb/calculate_tmb/calc_nonsyn_tmb.py
s