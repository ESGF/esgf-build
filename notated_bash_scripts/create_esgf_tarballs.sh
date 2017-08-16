#!/usr/local/bin/bash

#BASH ARGUMENT PASSED FROM COMMAND LINE IS starting_directory
source "$(dirname -- "$0")/script_version_attributes.sh"
#SCRIPT VERSION ATTRIBUTES ARE PULLED FROM BASH FILE
echo "script_maj_version: ${script_maj_version}"
echo "script_version: ${script_version}"
echo "script_release: ${script_release}"

####Do not change below this line####
replace_version='v2.0-RC5.4.0-devel'
replace_script_maj_version=2.0
replace_release='Centaur'
#TODO SUBSITUTE [.///...?] w/ ??????????????
quotedsv=`echo "$replace_version" | sed 's/[./*?|]/\\\\&/g'`;
quotedsr=`echo "$replace_release" | sed 's/[./*?|]/\\\\&/g'`;
quotedmj=`echo $replace_script_maj_version|sed 's/[./*?|]/\\\\&/g'`;

#THIS IS WRITING NOTHING TO LISTOFFILES? W/ NO NEWLINES????
echo -n >listoffiles;
#DECLARES A COMPONENTS DICTIONARY W/ REPO INDEX AND REPO INFO VALUE
declare -A components
components[esgf-dashboard]='bin/esg-dashboard dist/esgf_dashboard-0.0.2-py2.7.egg INSTALL README LICENSE'
components[esgf-desktop]='bin/esg-desktop INSTALL README LICENSE'
components[esgf-idp]='bin/esg-idp INSTALL README LICENSE'
components[esgf-installer]='jar_security_scan setup-autoinstall globus/esg-globus esg-bootstrap esg-node esg-init esg-functions esg-gitstrap esg-node.completion esg-purge.sh esg-autoinstall-testnode compute-tools/esg-compute-languages compute-tools/esg-compute-tools INSTALL README LICENSE'
components[esgf-node-manager]='bin/esg-node-manager bin/esgf-sh bin/esgf-spotcheck etc/xsd/registration/registration.xsd INSTALL README LICENSE'
components[esgf-security]='bin/esgf-user-migrate bin/esg-security bin/esgf-policy-check INSTALL README LICENSE'
#components[esgf-web-fe]='bin/esg-web-fe INSTALL README LICENSE'
components[esg-orp]='bin/esg-orp INSTALL README LICENSE'
components[esgf-getcert]='INSTALL README LICENSE'
components[esg-search]='bin/esg-search bin/esgf-crawl bin/esgf-optimize-index etc/conf/jetty/jetty.xml-auth etc/conf/jetty/realm.properties etc/conf/solr/schema.xml etc/conf/solr/solrconfig.xml etc/conf/solr/solrconfig.xml-replica etc/conf/solr/solr.xml-master etc/conf/solr/solr.xml-slave etc/conf/jetty/webdefault.xml-auth INSTALL README LICENSE'
components[esgf-product-server]='esg-product-server'
components[filters]='esg-access-logging-filter esg-drs-resolving-filter esg-security-las-ip-filter esg-security-tokenless-filters'
components[esgf-cog]='esg-cog'
components[esgf-stats-api]='bin/esg_stats-api_v2 dist/esgf-stats-api.war'
#REMOVE OLD DIRECTORIES FOR TARBALLS AND DISTS AND MAKES NEW
rm -rf esgf_tarballs
rm -rf temp-dists
mkdir esgf_tarballs
mkdir temp-dists
#TODO: ???????????????????????????????????????????????????????????
mkdir esgf-product-server 2>/dev/null
mkdir filters 2>/dev/null
mkdir esgf-cog 2>/dev/null
cp esgf-installer/product-server/* esgf-product-server/
cp esgf-installer/cog/esg-cog esgf-cog
cp esgf-installer/filters/* filters/
for i in "${!components[@]}"; do
	#IF THE REPO DOES NOT EXIST IT IS SKIPPED
	if [ ! -d $i ]; then
		echo "Directory $i not found. Bailing out.";
		continue;
	fi
	cp $i/dist/* temp-dists;
	rm temp-dists/ivy*.xml;
	#IF THE FILE IN THE COMPONENTS IS NOT FOUND SKIP
	for file in ${components[$i]}; do
		if [ ! -e $i/$file ]; then
			echo "File $i/$file not found";
			continue;
		else
			#IF FILE IS FOUND COPY TO temp-dists
			echo "File $i/$file OK";
			cp $i/$file temp-dists
		fi
	done
	#SEARCHES THE FILES LISTED AND IF MD5 IS FOUND SKIP
	cd temp-dists;
	for f in `ls`; do
		if echo $f|grep md5 >/dev/null; then
			continue;
		else
			#TODO:IF THE FILE IS ESG-NODE THEN ...............
			if [ "$f" = "esg-node" ]; then
				sed -i .backup "s/\(script_version=\"$quotedsv\"\)/script_version=\"$script_version\"/" esg-node;
				sed -i .backup "s/\(script_release=\"$quotedsr\"\)/script_release=\"$script_release\"/" esg-node;
				sed -i .backup "s/\(script_maj_version=\"$quotedmj\"\)/script_maj_version=\"$script_maj_version\"/" esg-node;
			fi
			if [ "$f" = "esg-bootstrap" ]; then
				sed -i .backup "s/\(script_maj_version=\"$quotedmj\"\)/script_maj_version=\"$script_maj_version\"/" esg-bootstrap;
			fi
			#???????????????????????????????????????????
			md5sum $f >$f.md5;
		fi
	 done
	if [ "$i" = "esgf-installer" ]; then
		echo "Found esgf-installer"
		mkdir $script_maj_version;
		mv esg-node* jar_security_scan* setup-autoinstall* esg-purge.sh* esg-init* esg-functions* esg-bootstrap* $script_maj_version/;
	fi
	#CREATES A TARBALL IN THE LISTED DIRECTORY
	tar -czf $i-dist.tgz *;
	mv $i-dist.tgz ../esgf_tarballs
	cd ..
	rm -rf temp-dists/*
	#LISTS THE CONTENTS OF THE TARBALL AND READS EACH LINE
	tar -tf esgf_tarballs/$i-dist.tgz |while read ln; do
		#TODO:??????????????????????????????????????????
		val=`echo $ln|sed '/\(.*\/$\)/d'`;
		echo "$i/$ln">>listoffiles;
	done
done
