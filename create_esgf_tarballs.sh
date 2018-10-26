#!/usr/local/bin/bash

source "$(dirname -- "$0")/script_version_attributes.sh"

echo "script_maj_version: ${script_maj_version}"
echo "script_sub_version: ${script_sub_version}"
echo "script_version: ${script_version}"
echo "script_release: ${script_release}"

####Do not change below this line####
replace_version="v2.6.0-devel-release"
replace_script_maj_version="2.6"
replace_script_sub_version="0"
replace_release="Name"
quotedsv=`echo "$replace_version" | sed 's/[./*?|]/\\\\&/g'`;
quotedsr=`echo "$replace_release" | sed 's/[./*?|]/\\\\&/g'`;
quotedmj=`echo "$replace_script_maj_version"|sed 's/[./*?|]/\\\\&/g'`;
quotedsubv=`echo "$replace_script_sub_version"|sed 's/[./*?|]/\\\\&/g'`;

quotedreplsv=`echo "$script_version"|sed 's/[./*?|]/\\\\&/g'`;
quotedreplsmv=`echo "$script_maj_version"|sed 's/[./*?|]/\\\\&/g'`;
quotedreplssv=`echo "$script_sub_version"|sed 's/[./*?|]/\\\\&/g'`;
quotedreplrel=`echo "$script_release"|sed 's/[./*?|]/\\\\&/g'`;

quotedipsl=`echo "distrib-coffee.ipsl.jussieu.fr/pub/esgf"|sed 's/[./*?|]/\\\\&/g'`;
quotedceda=`echo "dist.ceda.ac.uk/esgf"|sed 's/[./*?|]/\\\\&/g'`;
quotedaims=`echo "aims1.llnl.gov/esgf"|sed 's/[./*?|]/\\\\&/g'`;
quotedliu=`echo "esg-dn2.nsc.liu.se/esgf"|sed 's/[./*?|]/\\\\&/g'`;

cp postontag postontag-${script_maj_version}.${script_sub_version}_`date +%Y-%m-%d`
esgf_dist_mirrors_list=("dist.ceda.ac.uk/esgf" "aims1.llnl.gov/esgf" "esg-dn2.nsc.liu.se/esgf")
echo -n >listoffiles;
#Create dictionary of components
declare -A components
components[esgf-dashboard]='bin/esg-dashboard dist/esgf_dashboard-0.0.2-py2.7.egg INSTALL README LICENSE'
components[esgf-idp]='bin/esg-idp INSTALL README LICENSE'
components[esgf-installer]='jar_security_scan setup-autoinstall globus/esg-globus esg-bootstrap esg-node esg-init esg-functions esg-gitstrap esg-node.completion esg-purge.sh esg-autoinstall-testnode esg-autoinstall esg-autoinstall.template compute-tools/esg-compute-languages compute-tools/esg-compute-tools INSTALL README LICENSE esg-installarg CA.pl myproxy-server.config openssl.cnf'
components[esgf-node-manager]='bin/esg-node-manager bin/esgf-sh bin/esgf-spotcheck etc/xsd/registration/registration.xsd INSTALL README LICENSE'
components[esgf-security]='bin/esgf-user-migrate bin/esg-security bin/esgf-policy-check INSTALL README LICENSE'
#components[esgf-web-fe]='bin/esg-web-fe INSTALL README LICENSE'
components[esg-orp]='bin/esg-orp INSTALL README LICENSE etc/conf/esg-orp.properties'
components[esgf-getcert]='INSTALL README LICENSE'
components[esg-search]='bin/esg-search bin/esgf-crawl bin/esgf-optimize-index etc/conf/jetty/jetty.xml-auth etc/conf/jetty/realm.properties etc/conf/solr/schema.xml etc/conf/solr/solrconfig.xml etc/conf/solr/solrconfig.xml-replica etc/conf/solr/solr.xml-master etc/conf/solr/solr.xml-slave etc/conf/jetty/webdefault.xml-auth INSTALL README LICENSE solr-home.tar etc/conf/solr/log4j.properties'
components[esgf-product-server]='esg-las-config esg-product-server las_tds.xml.tmpl threddsConfig.xml.las'
components[filters]='dummylist'
components[esgf-cog]='esg-cog'
components[esgf-stats-api]='bin/esg_stats-api_v2 dist/esgf-stats-api.war'

#Delete esgf_tarballs and temp-dists directories
rm -rf esgf_tarballs
rm -rf temp-dists
rm -rf esgf-product-server
rm -rf filters
rm -rf esgf-cog

#Recreate esgf_tarballs and temp-dists directories
mkdir esgf_tarballs
mkdir -p temp-dists/$script_maj_version/$script_sub_version

#Make product-server, filters, and esgf-cog directory
mkdir esgf-product-server 2>/dev/null
mkdir filters 2>/dev/null
mkdir esgf-cog 2>/dev/null

#Copy product-server, esg-cog, and filters from esgf-installer to their own respective directories
cp esgf-installer/product-server/* esgf-product-server/
cp esgf-installer/cog/esg-cog esgf-cog
cp esgf-installer/filters/* filters/
cp -r dep-filters/* filters/
pushd esg-search/etc/conf
tar -cf solr-home.tar solr-home
popd
mv esg-search/etc/conf/solr-home.tar esg-search

for i in "${!components[@]}"; do
	if [ ! -d $i ]; then
		echo "Directory $i not found. Bailing out.";
		continue;
	fi
    mkdir -p temp-dists/$script_maj_version/$script_sub_version/$i
	#Copy the dist directory of a repo to temp-dists; The dist directory contains the jars,wars, and egg files
	cp $i/dist/* temp-dists/$script_maj_version/$script_sub_version/$i/;
	#Remove the ivy* files from temp-dists that just got copied over
	rm temp-dists/$script_maj_version/$script_sub_version/$i/ivy*.xml;
    
    if [ "$i" = "filters" ]; then #special handling for the filters files
        pushd tempdists/$script_maj_version/$script_sub_version/$i
        rm -rf .git;
        for f in `find . -type f`; do md5sum $f >$f.md5; done
        popd;
    fi

	for file in ${components[$i]}; do
		if [ ! -e $i/$file ]; then
			echo "File $i/$file not found";
			continue;
		else
			echo "File $i/$file OK";
			#Copy file to temp-dists
			#TODO: mkdir -p temp-dists/$i
			cp $i/$file temp-dists/$script_maj_version/$script_sub_version/$i/
		fi
	done

	pushd temp-dists/$script_maj_version/$script_sub_version/$i || exit;

	for f in *; do
        if [ "$i" = "filters" ]; then #we have already handled for the files in the filters directory
            break;
		#if file is a md5 hash; bypass it if so
		if echo $f|grep md5 >/dev/null; then
			echo "Skipping md5 file"
			continue;
		else
			if [ "$f" = "esg-node" ]; then
				echo "Found esg-node"
				sed -i "s/\(script_version=\"$quotedsv\"\)/script_version=\"$quotedreplsv\"/" esg-node;
				sed -i "s/\(script_release=\"$quotedsr\"\)/script_release=\"$quotedreplrel\"/" esg-node;
				sed -i "s/\(script_maj_version=\"$quotedmj\"\)/script_maj_version=\"$quotedreplsmv\"/" esg-node;
				sed -i "s/\(script_sub_version=\"$quotedsubv\"\)/script_sub_version=\"$quotedreplssv\"/" esg-node;
			fi
			if [ "$f" = "esg-bootstrap" ]; then
				echo "Found esg-bootstrap"
				sed -i "s/\(script_maj_version=\"$quotedmj\"\)/script_maj_version=\"$quotedreplsmv\"/" esg-bootstrap;
				sed -i "s/\(script_sub_version=\"$quotedsubv\"\)/script_sub_version=\"$quotedreplssv\"/" esg-bootstrap;
                cat esg-bootstrap|sed "s/$quotedipsl/$quotedliu/" >esg-bootstrap.liu && md5sum esg-bootstrap.liu >esg-bootstrap.liu.md5
                cat esg-bootstrap|sed "s/$quotedipsl/$quotedceda/" >esg-bootstrap.ceda && md5sum esg-bootstrap.ceda >esg-bootstrap.ceda.md5
                cat esg-bootstrap|sed "s/$quotedipsl/$quotedaims/" >esg-bootstrap.aims && md5sum esg-bootstrap.aims >esg-bootstrap.aims.md5
			fi
			#Create md5sum of file
			md5sum $f >$f.md5;
		fi
	done
    if [ "$i" = "esg-search" ]; then
        mkdir -p etc/conf/solr
        mv log4j.properties* etc/conf/solr/
    fi
    pushd ../../..
	tar -czf $i-dist.tgz *;
	mv $i-dist.tgz ../esgf_tarballs
	popd; popd
	rm -rf temp-dists/$script_maj_version/$script_sub_version/*
	tar -tf esgf_tarballs/$i-dist.tgz |while read ln; do
		val=`echo $ln|sed '/\(.*\/$\)/d'`;
		echo "$ln">>listoffiles;
	done
done
