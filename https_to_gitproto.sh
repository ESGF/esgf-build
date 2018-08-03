#!/bin/bash

while read ln; do
    cd $ln;
    line=`grep url .git/config`;
    quoted=`echo $line|sed 's/[./*?|#\t]/\\\\&/g'`;
    tgt='https://github.com/ESGF/'
    quotedtgt=`echo $tgt|sed 's/[/*?|#\t]/\\\\&/g'`;
    sed -i "s/$quotedtgt/git@github.com:ESGF\//" .git/config
    cd ..
done <repo_list.txt


