#!/usr/bin/env bash

cd /usr/local/bin
mkdir image-magick
yum -y groupinstall 'Development Tools'
yum -y install bzip2-devel freetype-devel libjpeg-devel libpng-devel libtiff-devel giflib-devel zlib-devel ghostscript-devel djvulibre-devel libwmf-devel jasper-devel libtool-ltdl-devel libX11-devel libXext-devel libXt-devel lcms-devel libxml2-devel librsvg2-devel OpenEXR-devel php-devel
wget http://www.imagemagick.org/download/ImageMagick.tar.gz
tar xvzf ImageMagick.tar.gz
cd ImageMagick*
./configure
make
make install
ldconfig /usr/local/lib
convert --version
ln -s /usr/local/bin/image-magick/convert /usr/bin/convert
export IMAGEMAGICK_BINARY=/usr/bin/convert
