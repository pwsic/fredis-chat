FROM ubuntu:xenial

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    nginx \
    supervisor \
    uwsgi \
    python-greenlet \
    python3-greenlet \
    uwsgi-plugin-tornado-python \
    uwsgi-plugin-greenlet-python \
    uwsgi-plugin-python \
    uwsgi-plugin-python3

#RUN useradd -ms /bin/bash uwsgi

EXPOSE 80 443 8000

ADD uwsgi.supervisor.conf /etc/supervisor/conf.d/uwsgi.conf
ADD host.conf /etc/nginx/sites-enabled/default
ADD uwsgi.ini /uwsgi.ini

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
