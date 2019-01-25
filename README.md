# ESGF Build

The ESGF Build script provides a convenient interface for building binary assets from multiple ESGF projects.  The script
has a command line interface for providing arguments as well as interactive prompts as a fallback.

The build process typically works as follows: checkout a branch/tag from GitHub -> pull the latest changes -> build the project -> (optionally) update the tag for the project -> (optionally) push the built assets to GitHub

### Prerequisites
1. Path to directory with repositories
2. Dependencies installed:
    * Python 2.7
    * Apache Ant
3. A .netrc file with a GitHub access token entry.  ESGF-Build uses the githubrelease python module under the hood and it uses token-based authentication.  See [Configuring githubrelease](https://github.com/j0057/github-release#configuring)

### Installing:
1. Clone the esgf-build repo ```git clone https://github.com/ESGF/esgf-build.git ```

2. Install the requirements using pip ```pip install -r requirements.txt```. Alternatively, if you are using a conda, there's
an conda environment file that can be used to create an ```esgf-build``` environment using the command ```conda env create -f environment.yml```

### Building With Script:
1. Run *esgf_build.py* by typing:
    ``` shell
    python esgf_build.py [repo_1 repos_2 ...repo_n]
    ```
  The esgf_build has command line arguments that can be passed to the script.
  ```shell
  --directory /path/to/repos
    Enter the path to the directory containing repositories on the system.
  --branch branch_name
    Choose which branch/tag you will be building from. Valid options are 'devel', 'master', or 'latest'. 'latest' builds from the most recent tag.
  --upload choice
    Choose whether to upload built assets to GitHub. Valid options are 'y', 'yes', 'n' or 'no'
```
 If any of the command line options are not passed to the script invocation, then the script will prompt for the user input.

2. Enter a title for the release when prompted.  
3. Enter 'yes' or 'no' when prompted to bump the version number.  You will be able to bump the version number according to the [Semantic Versioning](https://semver.org/) guidelines.

The script will then upload the binaries to the respective GitHub repositories.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/ESGF/esgf-build/tags).

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
