#!/bin/bash
if [ $# -eq 0 ]; then
	rsync -arWvu dist-repos/prod/ -e ssh --delete esgf@distrib-coffee.ipsl.jussieu.fr:/home/esgf/esgf/ 2>&1 |tee esgfupload.log
else
	rsync -arWvunO dist-repos/prod/ -e ssh --delete esgf@distrib-coffee.ipsl.jussieu.fr:/home/esgf/esgf/ 2>&1 |tee esgfupload.log
fi
