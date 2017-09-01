ESGF Build process
------------------
There are several steps in building an ESGF distribution.

1.  Fetching the code from Github

-   There is a function to purge the local repos and fetch fresh copies from Github

-   Another function can update all local repos listed in the configuration repo list to be in sync with the remote repos.  The user can choose either the devel or master branch to sync.

2.  Running the build scripts

-   Several of the ESGF subsystems are written in Java and are compiled using Ant.  These subsystem have a build.xml file in their repo that defines the build steps.

-   The major build steps in the build.xml file are as follows:

    *   clean

    *   pull

    *   make_dist

    *   publish

3. Creating a local mirror
Once the build process has completed, the binaries are placed in a directory that acts as a local mirror.  This local mirror will get RSynced with the remote distribution mirror

4. Upload to remote mirror
The local mirror will be synced to the main distribution mirror (distrib-coffee)
