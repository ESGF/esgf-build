#!/usr/local/bin/bash

#check correctness of paths
ANT=$(which ant)
JAVA_BINARY="$(dirname $(which java))"
JAVADIR=${JAVA_BINARY%/*}
echo "JAVA_DIR: ${JAVADIR}"
PYTHONDIR="$(dirname $(which python))"
echo "PYTHONDIR: ${PYTHONDIR}"
LOGDIR=$PWD/buildlogs

## v:export variables are available to other programs
##???????? A check for if there is a path to java and python and if not, then creates a path?
export JAVA_HOME=$JAVADIR
if ! echo $PATH|grep "$JAVADIR" >/dev/null; then
	echo "Will prepend path with custom java";
	export PATH=$JAVADIR:$PATH;
fi
##grep finds and searches for everything with pythondir in it and prints it to null (nowhere)
if ! echo $PATH|grep "$PYTHONDIR" >/dev/null; then
	echo "Will prepend path with custom python";
	export PATH=$PYTHONDIR:$PATH;
fi

#If no command line arguments; build all repos.  Otherwise build only repos passed as command line arguments
## v: $# prints the number of arguments passed to the shell script -eq checks for equality
if [ $# -eq 0 ]; then
	#Uses mapfile CLI tool that's part of Bash version 4
	##creates an array called fulllist and reads input from repo_list into it after finding repo_list in the current directory
	mapfile -t fulllist < "$(dirname -- "$0")/repo_list.txt"
	echo "fulllist: ${fulllist[*]}"
	echo
else
	## if there are command line arguments, then those are taken and used in fulllist
	fulllist=("${@:1}")
	echo "fulllist: ${fulllist[*]}"
	echo
fi


#################################################
##iterates over the array and logs <pwd>/buildlogs/<repositoryname>
for i in "${fulllist[@]}"; do
	##clean pull build logs are created (ANT)
	###opens 3 files
	echo -n >$LOGDIR/$i-clean.log
	echo -n >$LOGDIR/$i-pull.log
	echo -n >$LOGDIR/$i-build.log
	echo $i;
	cd $i;
	#if the esgf-getcert is buing built then
	if [ "$i" = "esgf-getcert" ]; then
		### pipes and uses tee to log the input to the defined log and sends it to ANT
		##the output of ant clean is redirected as the input of the log file
		$ANT clean 2>&1|tee $LOGDIR/$i-clean.log;
		$ANT dist 2>&1|tee $LOGDIR/$i-build.log;
		cd ..
		continue;
	fi
	$ANT clean_all 2>&1|tee $LOGDIR/$i-clean.log;
	$ANT pull 2>&1|tee $LOGDIR/$i-pull.log;
	$ANT make_dist 2>&1|tee $LOGDIR/$i-build.log;
	$ANT publish_local 2>&1|tee $LOGDIR/$i-publishlocal.log;
	cd ..
done

##recursively searches for build in all repos and logs the result
##prints out all the files with build in it
#Logs out the build result of all of the repos
grep -R "BUILD" buildlogs/esg*-*-build.log
