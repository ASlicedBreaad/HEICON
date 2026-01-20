#!/bin/bash

cd $(dirname $0)/..
source .venv/bin/activate
rm -rf linux/ build/

pyinstaller -y -D --upx-dir /usr/bin/upx --add-data debug_resources:debug_resources --add-data README.md:. -p .venv/lib/python3.14/site-packages/ --collect-submodules pillow --collect-submodules pillow_heif --contents-directory  modules --distpath linux heic_to_jpg.py

mv -f ./linux/heic_to_jpg/modules/debug_resources ./linux/heic_to_jpg/
mv -f ./linux/heic_to_jpg/modules/README.md ./linux/heic_to_jpg/

cd ./linux
zip -r "heic_to_jpg_linux.zip" ./*