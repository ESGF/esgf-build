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
echo -n >commits_since_last_tag.txt;
for i in "${fulllist[@]}"; do
	echo $i;
	echo $i >>taglist;
	echo "----------------------------" >>taglist;
	cd $i || return;
	git checkout $active_branch;
	git pull --tags;
	#list the commits since the last tag
	last_tag=$(git describe)
	git log $last_tag..HEAD>>../commits_since_last_tag.txt;
	git describe;
	git describe>>../taglist;
	echo
	printf $"\n">>taglist;
	echo "\n" >>taglist;
	cd ..
done
