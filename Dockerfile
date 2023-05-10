FROM python:3.10
WORKDIR "/usr/src/"
COPY . .
RUN python3.10 -m pip install --upgrade pip
RUN pip install poetry
RUN poetry self update
RUN /bin/true\
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction \
    && rm -rf /root/.cache/pypoetry
RUN python3.10 -m pip install setuptools

ARG HOSTNAME_DB=localhost
ARG USERNAME_DB=developer
ARG PASSWORD_DB=dev_password
ARG NAME_DB=disease-trend

CMD [ "gunicorn", "--workers=3", "--threads=3", "-b 0.0.0.0:8050", "main:app"]