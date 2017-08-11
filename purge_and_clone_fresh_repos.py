#!usr/bin/env python
import shutil
import repo_info
from git import Repo
import os
import re

#TODO: do not pass esgf-installer when not on personal computer

#Search for and remove appropriate repos
for repo in repo_info.REPO_LIST:
    if repo == 'esgf-installer':
        continue
    try:
        shutil.rmtree('/Users/brooks47/development/' + repo)
        print(repo + " removed succesfully.")
    except:
        print(repo + " does not exist on this system.")
        print( repo + " skipped.")


for repo_url in repo_info.ALL_REPO_URLS:
    #TODO: to make universal, allow user to enter the directory path to clone to

    ###In the future, if a module with more than 2 "-"s is created, this will
    ###need to be revised
    #strips.git from the string to make using reg-ex easier
    strip_repo = repo_url.replace(".git", "")
    directory_name = re.search('esg\w*-\w+\W*\w+', strip_repo).group()
    if directory_name == 'esgf-installer':
        continue
    print("Currently working on directory: " + directory_name)
    Repo.clone_from(repo_url, '/Users/brooks47/development/' + directory_name)
    print(directory_name + " succesfully cloned.")
