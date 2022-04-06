#!/bin/bash

cd ~/

##
## Prepare environment
##

# Get latest packages
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
if [[ ! -f "/etc/apt/sources.list.d/oibaf-ubuntu-graphics-drivers-jammy.list" ]];
then
    sudo add-apt-repository ppa:oibaf/graphics-drivers -y
    sudo apt-get update && sudo apt-get upgrade -y
fi
sudo apt-get install vainfo tar python3-pip -y
sudo apt-get install ffmpeg autoconf meson libtool -y
sudo apt-get install gstreamer-1.0 libgstreamer-plugins-base1.0-dev gstreamer1.0 gstreamer1.0-plugins-bad gstreamer1.0-tools gstreamer1.0-vaapi -y

export LIBVA_DRIVER_NAME=d3d12
export LIBVA_DRIVERS_PATH=/usr/lib/x86_64-linux-gnu/dri
export GST_VAAPI_ALL_DRIVERS=1
export D3D12_DEBUG="verbose debug"
export D3D12_VIDEO_ENC_CBR_FORCE_VBV_EQUAL_BITRATE=1
export ITU_T_ASSETS=~/repos/vaapi-fits/assets
export VAAPI_FITS_CONFIG_FILE=~/repos/vaapi-fits/config/d3d12_conformance
export D3D12_VAAPIFITS_IGNORE_EXITCODE=1

# Copy latest d3d12 libraries
sudo cp ~/d3d12libs/* /usr/lib/wsl/lib/

# Give user access to /dev/dri/* devices
sudo chmod 666 /dev/dri/*
curUser="`whoami`"
sudo usermod -a -G render "$curUser"
sudo usermod -a -G video "$curUser"

# Show vainfo on current system
vainfo --display drm --device /dev/dri/card0

# List gstreamer vaapi capabilities
rm -rf ~/.cache/gstreamer-1.0/*
gst-inspect-1.0 vaapi

##
## Unpack tests and assets
##

if [[ -d ~/repos ]];
then
    echo "~/repos directory exists. Using existing tests..."
else
	echo "~/repos directory does not exist. Cloning tests..."
    
    mkdir -p ~/repos
    pushd ~/repos

    if [[ ! -d ~/repos/vaapi-fits ]];
    then
        git clone https://github.com/sivileri/vaapi-fits.git
    fi

    pushd ~/repos/vaapi-fits

    git checkout user/sivileri/vaapifits_mesad3d12
    sudo pip3 install -r requirements.txt

    popd # ~/repos/vaapi-fits

    git clone https://github.com/intel-media-ci/gst-checksumsink
    pushd ~/repos/gst-checksumsink
    meson build -Dprefix=/usr
    sudo ninja -C build install
    popd # ~/repos/gst-checksumsink

    sudo apt-get install libva-dev -y
    git clone https://github.com/sivileri/libva-utils.git
    pushd ~/repos/libva-utils
    git checkout fix_vainfo_VAConfigAttribEncMaxSlices
    meson build
    sudo ninja -C build install
    # Delete ubuntu version so it falls back to /usr/local/bin/vainfo
    sudo rm /usr/bin/vainfo
    popd # ~/repos/libva-utils

    # Expand test assets
    mkdir -p ~/repos/vaapi-fits/assets
    tar -xvzf ~/assets.tar.gz -C ~/repos/vaapi-fits/assets

    popd # ~/repos
fi

pushd ~/repos/vaapi-fits

# Get latest tests playlists
git pull

# Delete previous results
rm -rf ~/repos/vaapi-fits/results

##
## Run all ffmpeg tests
##

python3 vaapi-fits run test/ffmpeg-vaapi/ --platform D3D12_WSL --artifact-retention 1 --device /dev/dri/renderD128

##
## Run all gstreamer tests
##

python3 vaapi-fits run test/gst-vaapi/ --platform D3D12_WSL --artifact-retention 1 --device /dev/dri/renderD128

popd # ~/repos/vaapi-fits
