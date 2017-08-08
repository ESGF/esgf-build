#!/bin/bash
if [ $# -eq 0 ]; then
	echo "prodn repo"
	rsync -arWvuh -e ssh --delete esgf@distrib-coffee.ipsl.jussieu.fr:/home/esgf/esgf/ $HOME/Development/dist-repos/prod/ 2>&1 |tee esgf-dist.log
	echo "now on to failsafe";
	rsync -arWvuh -e ssh esgf@distrib-coffee.ipsl.jussieu.fr:/home/esgf/esgf/ $HOME/Development/dist-repos/failsafe/
else
	echo "prodn repo"
	rsync -arWvunh -e ssh --delete esgf@distrib-coffee.ipsl.jussieu.fr:/home/esgf/esgf/ $HOME/Development/dist-repos/prod/ 2>&1 |tee esgf-dist.log
	echo "now on to failsafe";
	rsync -arWvunh -e ssh esgf@distrib-coffee.ipsl.jussieu.fr:/home/esgf/esgf/ $HOME/Development/dist-repos/failsafe/
fi
