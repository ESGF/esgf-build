#!/bin/bash

fulllist='esgf-dashboard esgf-desktop esgf-getcert esgf-idp esgf-installer esgf-node-manager esgf-publisher-resources esgf-security esg-orp esg-publisher esg-search'
echo -n >taglist;
active_branch='master'
for i in $fulllist; do
	echo $i;
	echo $i >>taglist;
	echo "----------------------------" >>taglist;
	cd $i;
	git checkout $active_branch;
	git merge devel;
	#git status;
	git describe; 
	git describe>>../taglist; 
	cd ..
done
