#!/usr/bin/env bash
ttab -w sudo /usr/local/sbin/rabbitmq-server start
source `which virtualenvwrapper.sh`
workon pondeye
ttab -w ./start_monaca.sh
celery -A scheduler worker -l info
