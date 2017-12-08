#!/usr/bin/env bash


yum install libjpeg-turbo-devel
yum install libpng-devel
yum install freetype-devel
cd /usr/local/bin
export EMAIL_PASSWORD='DaKuimcv1'
mkdir ffmpeg
wget  http://ffmpeg.gusari.org/static/64bit/ffmpeg.static.64bit.2014-03-02.tar.gz
tar -xzf ffmpeg.static.64bit.2014-03-02.tar.gz
ln -s /usr/local/bin/ffmpeg/ffmpeg /usr/bin/ffmpeg
export FFMPEG_BINARY=/usr/local/bin/ffmpeg/ffmpeg
pip install easy-thumbnails==2.4.1 django-image-cropping==1.0.4 moviepy==0.2.3.2
source /opt/python/current/env
sh install_image_magick.sh
mkdir