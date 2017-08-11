# Building With Script:
### What you will need:
1. Path to directory with repositories
    * Purge and clone script can be used to purge any existing repositories, and
clone new ones.
    * In the terminal, typing pwd in the directory of repositories will return the path.
2. Dependencies installed:
    * Python 2.7
    * Apache Ant

### To begin:
1. Navigate to the esgf-build repo in the terminal.
2. Run *esgf_build.py* by typing:
    ``` shell
    python esgf_build.py
    ```
3. Choose which branch you will be updating.
  (either devel or master)
4. Enter the path to the directory containing repositories on the system.
    * Example:
    ``` shell
    Users/username123/repositories
    ```
5. After the repositories update, then a menu of repos to build will be listed.
    * Type the index of the repo as shown in the menu into the terminal to
      select a repo. To select multiple repos, separate the indexes by commas.
    * Example:
    ``` shell
    0, 3, 4
    ```
    * Type nothing and hit [ENTER] to select all repos.
6. The build process will begin and old tarballs will be purged where applicable, then new tarballs will attempt to build. If successful, "BUILD SUCCESSFUL" will print.
7. Update the script info if it is different than the default shown.
8. Local mirror directory will be created if it does not already exist, and tarballs will be extracted to it.

COMING SOON
------------
9. Node will be updated with script settings and binaries to upload are validated.
10. Upload to coffee server.
