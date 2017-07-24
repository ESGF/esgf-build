Readme doc for setting up build environment and optionally the rsync mirror.
# Build Steps
1. Ensure that allrepos.txt and repo_list.txt is found and current.

2. Execute updateall.sh passing the branch to be updated as a command line argument to sequentially checkout the latest commit from the selected branch of each repo.
   * Example: 
   ``` shell 
   updateall.sh devel 
   ``` 
   * It also creates the taglist file, which you should check, to see if there are any commits after the last annotated tags.
      ``` shell 
      git log <yourlasttag>..HEAD 
      ``` 

3. If any retagging is needed, do so. Remember to use annotated tags. 
   * git tag -a '<version>' 'message'
   * ex: git tag -a 'v1.3.22-centaur-release' 'for whatever release'

4. Check paths to JAVA and PYTHON installation directories listed in buildall.sh. Use Sun Java 8 and Python 2.7

5. Execute buildall.sh to build repos using Ant.  This builds all repos by default, which can be time consuming.  To build a subset of repos, pass the names of the repos as command line arguments.
   * Example: 
   ``` shell
   buildall.sh esgf-dashboard esg-orp
   ```
   * The buildlogs will be printed out when the script finishes running.  All builds should be successful before moving forward.

6. Check values of script_maj_version, script_version and script_release in script_version_attributes.sh.  Update the version number as necessary.

7. Execute create_esgf_tarballs.sh.

At this point, you have the packaged tarballs in the esgf_tarballs directory. This is ready for extraction and upload to the dist mirror.



# Steps for extraction and upload to the dist-mirror 

1. Execute create_local_mirror_directory.sh with the distribution type as the command line argument to extract your freshly built binaries.
	* Example: 
	``` shell
	create_local_mirror_directory.sh [devel|master]
	```

2. Execute update-esgnode.sh by choosing what branch to use for the update (i.e update-esgnode.sh [devel|master]). 
	* Preferably, change the srcdir value to a clean clone of esgf-installer, which shouldn't have any unsaved changes.

3. Excute 'esgfupload.sh test' to check what files would be updated on coffee. Check in particular binary versions. Execute esgfupload.sh to push out the binaries to coffee. 
	* Trigger a local mirror update, with esgfdist.sh, to verify that both your mirror and coffee are in perfect sync.

Done!

Steps for optionally setting up a distribution mirror

1. esgfdist.sh sets up and updates a dist mirror that you run. If run without arguments, it actually performs an update; with any argument, it does a dry-run.
It assumes you have your ssh keys setup on coffee, for passwordless ssh.
IMPORTANT: always perform 'esgfdist.sh test' before you attempt to upload files.
