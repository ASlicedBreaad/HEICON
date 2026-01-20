#!/bin/bash

cd $(dirname $0)/..
source .venv/bin/activate
rm -rf windows/ build/
# Install wine and download Windows Python beforehand, create a .venv preferably 
wine .venv_windows/Scripts/python.exe -m PyInstaller -y --console --upx-dir /usr/bin/upx --add-data debug_resources:debug_resources --add-data README.md:. -p .venv_windows/Lib/site-packages/ --collect-submodules PIL --collect-submodules pillow_heif --contents-directory modules --distpath windows heic_to_jpg.py
mv -f ./windows/heic_to_jpg/modules/debug_resources ./windows/heic_to_jpg/
mv -f ./windows/heic_to_jpg/modules/README.md ./windows/heic_to_jpg/

cd ./windows
zip -r "heic_to_jpg_windows.zip" ./*