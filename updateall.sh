#!/usr/local/bin/bash

#Uses mapfile CLI tool that's part of Bash version 4
mapfile -t fulllist < "$(dirname -- "$0")/repo_list.txt"
echo "fulllist: ${fulllist[*]}"
echo

if [[ $1 == "devel" ]]; then
	active_branch='devel'
elif [[ $1 == "master" ]]; then
	active_branch='master'
else
	echo "Must choose a branch for repos to update (Primarily devel or master)"
	exit
fi
echo "active_branch: ${active_branch}"
echo

echo -n >taglist;
echo -n >gitloglist;
echo -n >ontags;
echo -n >postontag;

for i in "${fulllist[@]}"; do
	echo $i;
	echo $i >>taglist;
	echo "----------------------------" >>taglist;
	cd $i;
	git checkout $active_branch;
	git pull --tags;
	git describe; 
	git describe>>../taglist;
	echo -e "\n" >>../taglist;
    ontag=`git describe --abbrev=0`;
    echo "$i:$ontag" >>../ontags
    if [ "$i" != "esgf-installer" ]; then
        git checkout $ontag
        postot=`git describe`;
        echo "$i:$postot" >>../postontag
    fi
    echo "$i" >>../gitloglist
    git log -n 1 >>../gitloglist
	echo -e "\n" >>../gitloglist;
	cd ..
done
