#!/usr/bin/env bash

UP=$(pgrep mysql | wc -l);
if [ "$UP" -ne 1 ];
then
        echo "MySQL is down.";
else
        open -a PyCharm ~/DEVELOPMENT/tikedge/
        open -a Visual\ Studio\ Code ~/DEVELOPMENT/tikedge/pondeye/
        open -a Monaca\ Localkit
        cd ~/DEVELOPMENT/tikedge/
        echo "All is well.";
        source `which virtualenvwrapper.sh`
        workon pondeye
        chmod +rx ~/DEVELOPMENT/tikedge/start_monaca.sh
        chmod +rx ~/DEVELOPMENT/tikedge/start_celery.sh
        pip install -r requirements.txt
        ttab -w ./start_celery.sh
        python manage.py runserver 8100
fi





