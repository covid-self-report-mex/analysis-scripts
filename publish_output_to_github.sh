#!/usr/bin/env bash

# TO RUN THIS SCRIPT:
# - you need to have the right to publish in the targeted repo
# - you need to check the path...they are relative

# load .env vars
if [ -f .env ]
then
  export $(cat .env | sed 's/#.*//g' | xargs)
fi

OUTPUT_DIR='output_datasets/.'

# copy files
cp -R $OUTPUT_DIR/daily-reports $PUBLIC_DATASETS_REPO_RELATIVE_PATH
cp $OUTPUT_DIR/merge-all-days.csv $PUBLIC_DATASETS_REPO_RELATIVE_PATH

# move to the repo
cd $PUBLIC_DATASETS_REPO_RELATIVE_PATH

# print the timestamp (needed for the frontend)
now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo $now > last_update.txt

#push to github
git add .
git commit -m "update $now"
git push
