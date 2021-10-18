FROM python:3.10.0-bullseye

COPY requirements.txt /tmp/requirements.txt

RUN pip3 install -r /tmp/requirements.txt

COPY kdbx_headless __main__.py /opt

VOLUME /etc/kdbx-headless/
#fixme access dbus from host

WORKDIR /opt
ENTRYPOINT ["python3", "kdbx_headless"]
CMD []
