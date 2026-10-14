#!/bin/sh
# One command to publish: converts pictures, saves the change and uploads it to GitHub.
#   sh tools/publish.sh            (everything)    sh tools/publish.sh 13in3-a   (one screen)
cd "$(dirname "$0")/.." || exit 1
python3 tools/build_media.py "$@" || exit 1
git add -A
git commit -m "Update posters $(date '+%Y-%m-%d %H:%M')" || { echo "Nothing changed, nothing to upload."; exit 0; }
git push && echo "Published. Screens pick it up within about 5 minutes plus their current poster's minutes."
