#!/bin/bash
mkdir temp
export PYTHONPATH=./temp
/usr/bin/python setup.py build develop --install-dir ./temp
cp ./temp/AutoDL.egg-link ~/.config/deluge/plugins
rm -fr ./temp
