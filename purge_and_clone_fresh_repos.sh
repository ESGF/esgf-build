#!/bin/bash
#Deletes all existing repos and clones new copies

rm -rf ../esgf-dashboard ../esgf-desktop ../esgf-getcert ../esgf-idp ../esgf-node-manager ../esgf-publisher-resources ../esgf-security ../esgf-web-fe ../esg-orp ../esg-publisher ../esg-search ../esgf-stats-api

while read ln; do
	pushd ../
		git clone $ln;
	popd
done <allrepos.txt
