#!/bin/bash

buildmedia() {
  if [ -d "./site_media/static" ]; then
      echo "Remove site_media/static first"
      rm -rf ./site_media/static
  fi
  echo "Start to rebuild media"
  python manage.py build_media --all --interactive
  if [ $? -eq 0 ]; then
      echo "Media Built Successfully!"
  else
      echo "Failure: Are you running buildmedia in a django directory?"
  fi
}
