FROM python:3.10.0-bullseye

RUN useradd -rm -d /home/kdbxuser -s /bin/bash kdbxuser

COPY --chown=kdbxuser:kdbxuser requirements.txt /opt/kdbx-headless/requirements.txt

RUN pip3 install -r /opt/kdbx-headless/requirements.txt

COPY --chown=kdbxuser:kdbxuser . /opt/kdbx-headless/

RUN pip3 install -e /opt/kdbx-headless

VOLUME /etc/kdbx-headless/
VOLUME /etc/kdbx/

USER kdbxuser
WORKDIR /opt/kdbx-headless
ENTRYPOINT ["python3", "/opt/kdbx-headless/bin/kh.py"]
CMD [ "--ssl", "/etc/kdbx-headless/ssl", "--bind", "0.0.0.0" ]
