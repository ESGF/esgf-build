#!/bin/bash
#SUMMARY: goes in and updates esg-node with set script_version, etc and doing checks with md5sum
source "$(dirname -- "$0")/script_version_attributes.sh"

echo "script_maj_version: ${script_maj_version}"
echo "script_version: ${script_version}"
echo "script_release: ${script_release}"

echo $(pwd)

#jumps into directory and tries to checkout branch depending on active_directory
srcdir=./esgf-installer
pushd $srcdir

if [[ $1 == "devel" ]]; then
	active_branch='devel'
	git checkout devel;
elif [[ $1 == "master" ]]; then
	active_branch='master'
	git checkout master;
else
	echo "Must choose a branch for repos to update (Primarily devel or master)"
	exit
fi
git pull
#shows the most recent commit message (head shows top message, -5 shows first 5 lines)
git log|head -5
popd

##goes in and replaces old esg node settings (replace_version, etc) and replaces with
##what the user set for script_maj_version, etc
####Do not change below this line####
replace_version='v2.0-RC5.4.0-devel'
replace_release='Centaur'
replace_script_maj_version='2.0'
quotedsv=`echo "$replace_version" | sed 's/[./*?|]/\\\\&/g'`;
quotedsr=`echo "$replace_release" | sed 's/[./*?|]/\\\\&/g'`;
quotedmj=`echo "$replace_script_maj_version" | sed 's/[./*?|]/\\\\&/g'`;

if [ $active_branch == "devel" ]; then
	installerdir=$(pwd)/dist-repos/prod/dist/devel/esgf-installer/$script_maj_version
	lastpushdir=$(pwd)/dist-repos/prod/dist/devel
else
	installerdir=$(pwd)/dist-repos/prod/dist/esgf-installer/$script_maj_version
	lastpushdir=$(pwd)/dist-repos/prod/dist
fi
cat $srcdir/esg-node|sed "s/\(script_version=\"$quotedsv\"\)/script_version=\"$script_version\"/" >$installerdir/esg-node;
sed -i .backup "s/\(script_release=\"$quotedsr\"\)/script_release=\"$script_release\"/" $installerdir/esg-node;
sed -i .backup "s/\(script_maj_version=\"$quotedmj\"\)/script_maj_version=\"$script_maj_version\"/" $installerdir/esg-node;
cp $srcdir/esg-init $installerdir/esg-init
cp $srcdir/setup-autoinstall $installerdir/setup-autoinstall
allok=0
cd $installerdir && allok=1;
#md5sum (checksum) checks to makesure that what is being downloaded is what the user wants to download
if [ $allok -eq 1 ]; then
	md5sum esg-node >esg-node.md5;
	md5sum esg-init >esg-init.md5;
	md5sum setup-autoinstall >setup-autoinstall.md5
	dt=`date`;
	cd $lastpushdir
	echo $dt >lastpush;
	md5sum lastpush >lastpush.md5;
fi
