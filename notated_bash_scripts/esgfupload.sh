#!/bin/bash
#rsync does upload if no arguments are given, else does a dry run (-n makes dry run)
#TODO: make note of what all used options are doing
if [ $# -eq 0 ]; then
	#uses rsync to upload, and ssh into esgf coffee and if folder is deleted locally, deletes on coffee, piping log to file
	#TODO: have local mirror path be set by user (dist-repos/prod is hard coded location)
	rsync -arWvu dist-repos/prod/ -e ssh --delete esgf@distrib-coffee.ipsl.jussieu.fr:/home/esgf/esgf/ 2>&1 |tee esgfupload.log
else
	rsync -arWvunO dist-repos/prod/ -e ssh --delete esgf@distrib-coffee.ipsl.jussieu.fr:/home/esgf/esgf/ 2>&1 |tee esgfupload.log
fi
