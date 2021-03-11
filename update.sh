#!/usr/bin/env bash
set -e
# Simple bash script which:
# 1. Downloads the data CSV of yesterday
# 2. Generates the numbers per municipality and dumps them to a JSON file in the Hugo directory
# 3. Tries to build the Hugo website
# 4. Commit new data to git and push
# 5. AWS Amplify will automatically re-deploy

if [ "$(git status --porcelain)" ]; then
  echo "Warning: Git is not clean. Commit your changes first."
  exit 1
fi

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
