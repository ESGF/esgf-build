#!/usr/local/bin/bash
declare -A dists
dists[esgf-dashboard-dist.tgz]='esgf-dashboard'
dists[esgf-getcert-dist.tgz]='esgf-getcert'
dists[esgf-idp-dist.tgz]='esgf-idp'
dists[esgf-installer-dist.tgz]='esgf-installer'
dists[esgf-node-manager-dist.tgz]='esgf-node-manager'
dists[esgf-security-dist.tgz]='esgf-security'
dists[esg-orp-dist.tgz]='esg-orp'
dists[esg-search-dist.tgz]='esg-search'
dists[esgf-product-server-dist.tgz]='esgf-product-server'
dists[esgf-cog-dist.tgz]='esgf-cog'
dists[filters-dist.tgz]='filters'
dists[esgf-stats-api-dist.tgz]='esgf-stats-api'

source "$(dirname -- "$0")/script_version_attributes.sh"

echo "script_maj_version: ${script_maj_version}"
echo "script_sub_version: ${script_sub_version}"
echo "script_version: ${script_version}"
echo "script_release: ${script_release}"

if [[ $1 == "devel" ]]; then
	distribution_type='devel'
elif [[ $1 == "master" ]]; then
	distribution_type='master'
else
	echo "Must choose a distribution type for repos to update (devel or master)"
	exit
fi

for i in "${!dists[@]}"; do
	tgtdir=${dists[$i]};

	if [ $distribution_type == "devel" ]; then
		cp esgf_tarballs/$i dist-repos/prod/dist/devel/;
		pushd dist-repos/prod/dist/devel/;
		echo "Extracting ${i} -> $(pwd)" 
		tar -xvzf $i && rm -f $i;
		echo
        pushd $script_maj_version/$script_sub_version
        ln -s ../../../java java
        ln -s ../../../lists lists
        ln -s ../../../externals externals
        ln -s ../../../geoip geoip
        ln -s ../../../thredds thredds
        ln -s ../../../robots.txt robots.txt
        ln -s ../../../favicon.ico favicon.ico
        popd; popd
	else 
		cp esgf_tarballs/$i dist-repos/prod/dist/;
		pushd dist-repos/prod/dist/;
		echo "Extracting ${i} -> $(pwd)"
		tar -xvzf $i && rm -f $i;
		echo
        pushd $script_maj_version/$script_sub_version
        ln -s ../../../java java
        ln -s ../../../lists lists
        ln -s ../../../externals externals
        ln -s ../../../geoip geoip
        ln -s ../../../thredds thredds
        ln -s ../../../robots.txt robots.txt
        ln -s ../../../favicon.ico favicon.ico
        popd; popd
	fi
done
