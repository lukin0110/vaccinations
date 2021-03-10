#!/usr/bin/env bash
set -e

# TODO: check if git is clean
yesterday=$(date -j -v-1d +'%d-%m-%Y')
python scripts/process.py fetch ${yesterday}
python scripts/process.py crunch

# Check if the website can be build with Hugo
cd website
hugo -D --minify
cd ..

git add data/ website/data/
git commit -m "Update ${yesterday}"
git push
