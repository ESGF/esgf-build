#!/bin/bash
#Deletes all existing repos and clones new copies

####use shutil.rmtree in python to delete these repos, but exclude esgf-installer
rm -rf esgf-dashboard esgf-desktop esgf-getcert esgf-idp esgf-installer esgf-node-manager esgf-publisher-resources esgf-security esgf-web-fe esg-orp esg-publisher esg-search


###loop over all the repos in the repo list and use git module to clone them
while read ln; do
	git clone $ln;
done <allrepos.txt
