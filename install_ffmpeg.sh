#!/usr/bin/env bash


yum install libjpeg-turbo-devel
yum install libpng-devel
yum install freetype-devel
eb ssh -i i-0ef773441e3e03659
sudo su -
cd /usr/local/bin
mkdir ffmpeg
wget ffmpeg.static.64bit.2014-03-02.tar.gz
tar -xzf ffmpeg.static.64bit.2014-03-02.tar.gz
ln -s /usr/local/bin/ffmpeg/ffmpeg /usr/bin/ffmpeg
export FFMPEG_BINARY=/usr/bin/ffmpeg

