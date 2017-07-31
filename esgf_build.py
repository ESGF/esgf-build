#!usr/bin/env python
'''Modules needed mostly to access terminal commands'''
import subprocess
import shlex
import os
import glob
import time
from distutils.spawn import find_executable
import tarfile
import mmap
from git import Repo
import repo_info

#TODO: create a list of repos to exclude from building

#repo_info.all_repo_urls
#repo_info.repo_list

def update_all(active_branch, starting_directory):
    '''Checks each repo in the repo_list for the most updated branch '''
    ##taglist will keep track of different versions
    print "Beginning to update directories"
    fileobject = open("taglist", "w")
    for repo in repo_info.repo_list:
        try:
            os.chdir(starting_directory + "/" + repo)
        except OSError:
            print "Directory does not exist"
        #getting the current working directory (mimics bash pwd)
        repo_handle = Repo(os.getcwd())
        #changes to the active branch using checkout
        repo_handle.git.checkout(active_branch)
        repo_handle.remotes.origin.pull()
        print "Updating: " + repo
        #provides all the tags, reverses them (so that you can get the latest
        #tag) and then takes only the first from the list
        tag_list = repo_handle.tags
        new_tag_list = list(tag_list)
        new_tag_list.reverse()
        latest_tag = str(new_tag_list[0])
        fileobject.write(latest_tag)
        #moves up one directory
        os.chdir("..")
    fileobject.close()
    print "Directory updates complete."

def build_all(build_list, starting_directory):
    '''Takes a list of repositories to build, and uses ant to build them '''
    #use subprocess for ANT
    #locate the paths for ANT, java, and python
    ant_path = find_executable('ant')
    java_path = find_executable('java')
    python_path = find_executable('python')

    #TODO: find out what should be done with these paths?
    #logs will be saved at the starting directory in the folder buildlogs
    log_directory = starting_directory + "/buildlogs"
    #creates a directory for the logs in the system if one does not exist
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    for repo in build_list:
        #TODO: include installer in build script for final version
        if repo == 'esgf-installer':
            continue
        #TODO: add esgf-publisher-resources and publisher to a list of exclusions
        if repo == 'esgf-publisher-resources':
            continue
        if repo == 'esg-publisher':
            continue
        print "Building repo: " + repo
        #the directory is changed to the repo directory
        #in order to call ant on the build.xml file in the directory
        os.chdir(starting_directory + "/" + repo)
        #repos getcert and stats-api do not need an ant pull call
        if repo == 'esgf-getcert':
            #calls ant_clean for esgf-getcert
            clean_log = log_directory + "/" + repo + "-clean.log"
            with open(clean_log, "w") as fgc1:
                ant_clean = subprocess.check_output(shlex.split('{ant} clean'.format(ant=ant_path)))
                fgc1.write(ant_clean)
            #calls ant dist for esgf-getcert
            build_log = log_directory + "/" + repo + "-build.log"
            with open(build_log, "w") as fgc2:
                ant_dist = subprocess.check_output(shlex.split('{ant} dist'.format(ant=ant_path)))
                fgc2.write(ant_dist)
            os.chdir("..")
            continue
        if repo == 'esgf-stats-api':
            # clean_log = log_directory + "/" + repo + "-clean.log"
            # with open(clean_log, "w") as fsapi1:
            #     ant_cleanall = subprocess.check_output(shlex.split('{ant} clean_all'.format(ant=ant_path)))
            #     fsapi1.write(ant_cleanall)
            # build_log = log_directory + "/" + repo + "-build.log"
            # with open(build_log, "w") as fsapi2:
            #     ant_make = subprocess.check_output(shlex.split("{ant} make_dist".format(ant = ant_path)))
            #     fsapi2.write(ant_make)
            # os.chdir('..')
            continue
        #calls and logs the ant clean_all comamnd
        clean_log = log_directory + "/" + repo + "-clean.log"
        with open(clean_log, "w") as file1:
            ant_cleanall = subprocess.check_output(shlex.split('{ant} clean_all'.format(ant=ant_path)))
            file1.write(ant_cleanall)
        #calls and logs the ant pull command
        pull_log = log_directory + "/" + repo + "-pull.log"
        with open(pull_log, "w") as file2:
            ant_pull = subprocess.check_output(shlex.split('{ant} pull'.format(ant = ant_path)))
            file2.write(ant_pull)
        #calls and logs the ant make_dist command
        build_log = log_directory + "/" + repo + "-build.log"
        with open(build_log, "w") as file3:
                ant_make = subprocess.check_output(shlex.split("{ant} make_dist".format(ant = ant_path)))
                file3.write(ant_make)
        os.chdir("..")
    print "Repository builds complete."

    print "Finding esgf log files."
    #uses glob to find all esgf log files
    #then iterates over the log files , opens them
    #and uses a mmap object to search through for BUILD reference
    #returns the ones with BUILD references to be checked by a script during build
    all_logs = glob.glob('buildlogs/esg*-*-build.log')
    for log in all_logs:
        with open(log) as flog:
            mmap_object = mmap.mmap(flog.fileno(), 0, access=mmap.ACCESS_READ)
            if mmap_object.find('BUILD') != -1:
                return log

def create_esgf_tarballs():
    #import tarfile
    pass

def create_local_mirror_directory(active_branch):
    pass

def update_esg_node(active_branch):
    pass

def esgf_upload():
    pass


def main():
    '''User prompted for build specifications '''
    #Use a raw_input statement to ask the user if they want to update devel or master
    #The user's answer will set the active_branch variable; must either be devel or master
    while True:
        active_branch = raw_input("Do you want to update devel or master branch? ")

        #Run the update_all(active_branch) function, passing in active_branch as an argument
        if active_branch.lower() not in ["devel", "master"]:
            print "Please choose either master or devel."
            continue
        else:
            break

    while True:
        #check if the directory exists, if not build it then get absolute path
        starting_directory = raw_input("Please provide the path to the repositories on your system: ").strip()
        if os.path.isdir(os.path.realpath(starting_directory)):
            starting_directory = os.path.realpath(starting_directory)
            break
        else:
            create_path_q = raw_input("The path does not exist. Do you want " + starting_directory + " to be created? (Y or YES)")
            if create_path_q.lower() not in ["yes", "y"]:
                print "Not a valid response. Directory not created."
                continue
            else:
                os.makedirs(starting_directory)
                starting_directory = os.path.realpath(starting_directory)
                break

    update_all(active_branch, starting_directory)

    #Use a raw_input statement to ask which repos should be built;
    #this will set the build_list variable; If the user enters nothing,
    #assume all repos will be built
    while True:
        build_list = raw_input("Which repositories will be built? (Hit [Enter] for all) ")

        if not build_list:
            all_repo_q = raw_input("Do you want to build all repositories? (Y or YES) ")
            if all_repo_q.lower() not in ["yes", "y"]:
                print "Not a valid response."
                continue

            else:
                build_list = repo_info.repo_list
                break
    build_all(build_list, starting_directory)

    #Use a raw_input statement to ask the user to set the script_major_version, script_release, and
    #script_version
    script_major_version = raw_input("Please set the script_major_version: ")
    script_release = raw_input("Please set the script_release: ")
    script_version = raw_input("Please set the script version: ")

    #execute the create_esgf_tarballs() function

    #execute the create_local_mirror_directory(active_branch), passing in
    #active_branch as an argument

    #execute update_esg_node(active_branch), passing in active_branch as an argument

    #execute esgf_upload()

if __name__ == '__main__':
    main()
