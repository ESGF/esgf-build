#!/bin/bash
#Deletes all existing repos and clones new copies

rm -rf esgf-dashboard esgf-desktop esgf-getcert esgf-idp esgf-installer esgf-node-manager esgf-publisher-resources esgf-security esgf-web-fe esg-orp esg-publisher esg-search

while read ln; do 
	git clone $ln;
done <allrepos.txt
