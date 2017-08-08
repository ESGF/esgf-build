#!/bin/bash
if [ $# -eq 0 ]; then
	rsync -arWvu $HOME/Development/dist-repos/prod/ -e ssh --delete root@esgf-dev2.llnl.gov:/home/esgf/esgf/ 2>&1 |tee esgfupload.log
else
	rsync -arWvunO  $HOME/Development/dist-repos/prod/ -e ssh --delete root@esgf-dev2.llnl.gov:/home/esgf/esgf/ 2>&1 |tee esgfupload.log


fi
