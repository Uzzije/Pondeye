
#!/usr/bin/env bash

# python ../manage.py dumpdata --indent 4 --exclude=contenttypes --exclude=auth.Permission -o base-data.json

MYSQL=`which mysql`

Q1="DROP DATABASE tikedge_db;"
SQL="${Q1}"
$MYSQL -u root -p -e "$SQL"

sh createdb.sh tikedge_db tikedge_user tikedge_user

rm -f ../apps/social/migrations/*
rm -f ../apps/tasks/migrations/*
touch ../apps/social/migrations/__init__.py
touch ../apps/tasks/migrations/__init__.py
python ../manage.py makemigrations
python ../manage.py migrate

# python ../manage.py loaddata base-data.json
# mv base-data.json ../../relevate_web_app/
