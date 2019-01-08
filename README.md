# Building With Script:
### What you will need:
1. Path to directory with repositories
2. Dependencies installed:
    * Python 2.7
    * Apache Ant
3. A .netrc file with a GitHub access token entry.  ESGF-Build uses the githubrelease python module under the hood and it uses token-based authentication.  See [Configuring githubrelease](https://github.com/j0057/github-release#configuring)

### To begin:
1. Clone the esgf-build repo ```git clone https://github.com/ESGF/esgf-build.git ```
2. Install the requirements using pip ```pip install -r requirements.txt```
2. Run *esgf_build.py* by typing:
    ``` shell
    python esgf_build.py
    ```
3. Choose which branch/tag you will be building from. Valid options are ```devel```, ```master```, or ```latest```. 'latest' builds from the most recent tag.
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
6. The build process will begin. A build status report will be logged to the screen once all the builds have concluded.
7. Enter 'yes' or 'no' when prompted if you would like to upload assets to GitHub.
8. Enter a title for the release when prompted.  
9. Enter 'yes' or 'no' when prompted to bump the version number.  You will be able to bump the version number according to the [Semantic Versioning](https://semver.org/) guidelines.

The script will then upload the binaries to the respective GitHub repositories.
