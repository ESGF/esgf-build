#!/bin/bash

echo -n >taglist
while read ln; do
    repo=`echo $ln|cut -d':' -f1`;
    tag=`echo $ln|cut -d':' -f2`;
    cd $repo
    git checkout master && git pull
    git merge $tag
    git push
    nt=`git describe`
    echo "$repo:$nt">>../taglist
    cd ..
done <postontag
