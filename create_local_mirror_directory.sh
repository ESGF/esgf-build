#!/usr/local/bin/bash
declare -A dists
dists[esgf-dashboard-dist.tgz]='esgf-dashboard'
dists[esgf-desktop-dist.tgz]='esgf-desktop'
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
        if [ ! -d dist-repos/prod/dist/devel/$tgtdir/ ]; then
        	mkdir -p dist-repos/prod/dist/devel/$tgtdir/
        fi
        if [ ! -d dist-repos/prod/dist/$tgtdir/ ]; then
                mkdir -p dist-repos/prod/dist/$tgtdir/
        fi
	if [ $distribution_type == "devel" ]; then
		cp esgf_tarballs/$i dist-repos/prod/dist/devel/$tgtdir/;
		cd dist-repos/prod/dist/devel/$tgtdir;
		echo "Extracting ${i} -> $(pwd)" 
		tar -xvzf $i && rm -f $i;
		echo
	else 
		cp esgf_tarballs/$i dist-repos/prod/dist/$tgtdir/;
		cd dist-repos/prod/dist/$tgtdir;
		echo "Extracting ${i} -> $(pwd)"
		tar -xvzf $i && rm -f $i;
		echo
	fi
	if [ "$tgtdir" = "esgf-installer" ]; then
		mv esg-globus* ../externals/bootstrap/
	fi
	
	cd - 
done
