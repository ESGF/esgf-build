# Building With Script:
### What you will need:
1. Path to directory with repositories
2. Dependencies installed:
    * Python 2.7
    * Apache Ant
3. A .netrc file with a GitHub access token entry.  ESGF-Build uses the githubrelease python module under the hood and it uses token-based authentication.  See [Configuring githubrelease](https://github.com/j0057/github-release#configuring)

### To begin:
1. Clone the esgf-build repo ```git clone https://github.com/ESGF/esgf-build.git ```
   * Optional step: Create a conda environment or virtual environment for dependencies.
2. Install the requirements using pip ```pip install -r requirements.txt```
3. Run *esgf_build.py* by typing:
    ``` shell
    python esgf_build.py [repo_1 repos_2 ...repo_n]
    ```
  The esgf_build has command line arguments that can be passed to the script.
  ```shell
  --directory /path/to/repos
    Enter the path to the directory containing repositories on the system.
  --branch branch_name
    Choose which branch/tag you will be building from. Valid options are 'devel', 'master', or 'latest'. 'latest' builds from the most recent tag.
  --bump version_component
    Bump the version number according to the Semantic Versioning specification. Valid options are 'major', 'minor', or 'patch'. Leaves version unchanged if option is omitted.
  --name release_name
    Enter a name for the release.  The release will default to tag number as the name if this option is omitted.
  --prerelease
    Boolean flag for tagging the release a nonproduction. Defaults to False if omitted
  --dryrun
    Boolean flag for performing a dry run of the release. Defaults to False if omitted
  --upload/--no-upload
    Boolean flag to choose whether to upload built assets to GitHub.
```
If any of the command line options are not passed to the script invocation, then the script will prompt for the user input.
