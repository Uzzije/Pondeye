pip install django-image-cropping
pip install easy_thumbnails
pip install moviepy
MYSQL=`which mysql`


sh createdb.sh tikedge_db tikedge_user tikedge_user
if [ -f ../apps/social/migrations/0001_initial.py ]; then
    cd ..
    python manage.py migrate
fi
python download_moviepy.py