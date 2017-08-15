#!/usr/local/bin/bash

#check correctness of paths
ANT=$(which ant)
JAVA_BINARY="$(dirname $(which java))"
JAVADIR=${JAVA_BINARY%/*}
echo "JAVA_DIR: ${JAVADIR}"
PYTHONDIR="$(dirname $(which python))"
echo "PYTHONDIR: ${PYTHONDIR}"
LOGDIR=$PWD/buildlogs

mkdir -p $LOGDIR

export JAVA_HOME=$JAVADIR
if ! echo $PATH|grep "$JAVADIR" >/dev/null; then
	echo "Will prepend path with custom java";
	export PATH=$JAVADIR:$PATH;
fi
if ! echo $PATH|grep "$PYTHONDIR" >/dev/null; then
	echo "Will prepend path with custom python";
	export PATH=$PYTHONDIR:$PATH;
fi

#If no command line arguments; build all repos.  Otherwise build only repos passed as command line arguments
if [ $# -eq 0 ]; then
	#Uses mapfile CLI tool that's part of Bash version 4
	mapfile -t fulllist < "$(dirname -- "$0")/repo_list.txt"
	echo "fulllist: ${fulllist[*]}"
	echo
else
	fulllist=("${@:1}")
	echo "fulllist: ${fulllist[*]}"
	echo
fi


for i in "${fulllist[@]}"; do
	echo -n >$LOGDIR/$i-clean.log
	echo -n >$LOGDIR/$i-pull.log
	echo -n >$LOGDIR/$i-build.log


	#Timing without building esgf-desktop
	#real	9m34.689s
	#user	2m34.351s
	#sys	0m13.850s

	#Timing with building esgf-desktop
	# real	16m27.802s
	# user	2m53.092s
	# sys	0m16.969s

	#Ignore directories without a build.xml file
	if [ "$i" = "esgf-installer" ] || [ "$i" = "esgf-publisher-resources" ] || [ "$i" = "esgf-desktop" ] || [ "$i" = "esg-publisher" ]; then
		continue;
	fi

	echo
	echo "*******************************"
	echo "Building  ${i}"
	echo "*******************************"
	echo

	cd $i || exit;

	if [ "$i" = "esgf-getcert" ]; then
		$ANT clean 2>&1|tee $LOGDIR/$i-clean.log;
		$ANT dist 2>&1|tee $LOGDIR/$i-build.log;
		cd ..
		continue;
	fi

	if [ "$i" = "esgf-stats-api" ]; then
		#Makes call to clean_all target in the build.xml file; (Cleans out generatable artifacts)
		$ANT clean_all 2>&1|tee $LOGDIR/$i-clean.log;
		#Makes call to pull target in the build.xml file; Git clone ESGF Maven Repositories from Github
		$ANT make_dist 2>&1|tee $LOGDIR/$i-build.log;
		#Makes call to publish_local in the build.xml file; (publishes built artifacts to remote repository: https://github.com/ESGF/esgf-artifacts)
		cd ..
		continue;
	fi

	#Makes call to clean_all target in the build.xml file; (Cleans out generatable artifacts)
	$ANT clean_all 2>&1|tee $LOGDIR/$i-clean.log;
	#Makes call to pull target in the build.xml file; Git clone ESGF Maven Repositories from Github
	$ANT pull 2>&1|tee $LOGDIR/$i-pull.log;
	#Makes call to make_dist in the build.xml file; (Creates full software distribution)
	$ANT make_dist 2>&1|tee $LOGDIR/$i-build.log;
	#Makes call to publish_local in the build.xml file; (publishes built artifacts to remote repository: https://github.com/ESGF/esgf-artifacts)
	$ANT publish_local 2>&1|tee $LOGDIR/$i-publishlocal.log;
	cd ..
done

#Logs out the build result of all of the repos
grep -R "BUILD" buildlogs/esg*-*-build.log


grep -R "Total time" buildlogs/esg*-*-build.log
