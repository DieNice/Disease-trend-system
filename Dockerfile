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

CMD [ "gunicorn", "--workers=3", "--threads=3", "-b 0.0.0.0:8050", "main:server"]