@echo off
mkdir temp
set PYTHONPATH=.\temp
"C:\Python27\python.exe" setup.py build develop --install-dir .\temp
cp .\temp\autodl.egg-link "%appdata%\deluge\plugins"
rm -fr ./temp
