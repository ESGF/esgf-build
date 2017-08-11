#!usr/bin/env python
'''Modules needed mostly to access terminal commands'''
import subprocess
import shlex
import os
import shutil
import glob
import errno
from distutils.spawn import find_executable
import tarfile
import mmap
from git import Repo
import repo_info

#TODO: create a list of repos to exclude from building

def update_all(active_branch, starting_directory):
    '''Checks each repo in the REPO_LIST for the most updated branch '''
    ##taglist will keep track of different versions
    print "Beginning to update directories."
    fileobject = open("taglist", "w")
    for repo in repo_info.REPO_LIST:
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
    #TODO: use subprocess w/ bash command to set the java and python paths
    ant_path = find_executable('ant')
    #java_path = find_executable('java')
    #python_path = find_executable('python')
    #logs will be saved at the starting directory in the folder buildlogs
    log_directory = starting_directory + "/buildlogs"
    #creates a directory for the logs in the system if one does not exist
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    for repo in build_list:
        #TODO: add loading bar while ant runs?
        #TODO: include installer in build script for final version
        if repo == 'esgf-installer':
            continue
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
                stream_subprocess_output('{ant} clean'.format(ant=ant_path), fgc1)
            #calls ant dist for esgf-getcert
            build_log = log_directory + "/" + repo + "-build.log"
            with open(build_log, "w") as fgc2:
                stream_subprocess_output('{ant} dist'.format(ant=ant_path), fgc2)

            os.chdir("..")
            continue
        if repo == 'esgf-stats-api':
            clean_log = log_directory + "/" + repo + "-clean.log"
            with open(clean_log, "w") as fsapi1:
                stream_subprocess_output('{ant} clean_all'.format(ant=ant_path), fsapi1)
            build_log = log_directory + "/" + repo + "-build.log"
            with open(build_log, "w") as fsapi2:
                stream_subprocess_output("{ant} make_dist".format(ant=ant_path), fsapi2)
            os.chdir('..')
            #print "Repo not built:"
            continue
        #calls and logs the ant clean_all comamnd
        clean_log = log_directory + "/" + repo + "-clean.log"
        with open(clean_log, "w") as file1:
            stream_subprocess_output('{ant} clean_all'.format(ant=ant_path), file1)
        #calls and logs the ant pull command
        pull_log = log_directory + "/" + repo + "-pull.log"
        with open(pull_log, "w") as file2:
            stream_subprocess_output('{ant} pull'.format(ant=ant_path), file2)
        #calls and logs the ant make_dist command
        build_log = log_directory + "/" + repo + "-build.log"
        with open(build_log, "w") as file3:
            stream_subprocess_output("{ant} make_dist".format(ant=ant_path), file3)
        os.chdir("..")
    print "\nRepository builds complete."

    print "Finding esgf log files.\n"
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

def create_esgf_tarballs(starting_directory, build_list):
    #TODO: how should I be using the dists that were created?
    ##### is adding the repos to the tarball correct?
    ##### or should i be using something from build func?
    #creating a directory to save the tarballs to
    #import pdb; pdb.set_trace()

    tarball_dir = starting_directory + "/esgf_tarballs"
    print "Attempting to remove old tarballs."
    try:
        shutil.rmtree(tarball_dir)
        print "Old tarballs removed, beginning to create tarballs."
    except:
        print "No old tarballs located, beginning to create tarballs."
    os.makedirs(tarball_dir)
    #TODO: pass in the build_list to only build tarballs for specified repos
    for repo in build_list:
        #each tarball will have it's own directory in the main tarball directory
        local_tarball_dir = os.path.join(tarball_dir, repo)
        #the path to the repo to create a tar of
        repo_path = os.path.join(starting_directory, repo)
        repo_path = os.path.realpath(repo_path)
        #changing directory to that repo to tar it
        #import pdb; pdb.set_trace()
        os.chdir(tarball_dir)
        with tarfile.open(local_tarball_dir + ".tgz", "w:gz") as tar:
            #tar.add("../" + repo)
            tar.add(repo_path, arcname=repo)
        print repo + " tarball created."
        os.chdir("..")

def create_local_mirror_directory(active_branch, starting_directory):
    '''Creates a directory for binaries and untars to it'''
    #if active_branch is devel then copy to dist folder for devel
    #if active_branch is master then copy to dist folder
    #untar in dist and delete tarballs
    print "Creating local mirrror directory."
    #TODO: realpath stuff
    mkdir_p('../esgf_bin')
    os.chdir('esgf_tarballs')
    #goes to each tarball listed in the tarballs directory
    for tarball in os.listdir(os.getcwd()):
        tar = tarfile.open(tarball)
        tar.extractall(path="../esgf_bin")
        tar.close()
    print "Tarballs extracted to directory."

def update_esg_node(active_branch, starting_directory, script_major_version,
                    script_release, script_version):
    srcdir = 'esgf-installer'

    if active_branch == 'devel':
        installerdir = (starting_directory
                        +'/dist-repos/prod/dist/devel/esgf-installer/'
                        + script_major_version)
    else:
        installerdir = (starting_directory
                        + '/dist-repos/prod/dist/esgf-installer/'
                        + script_major_version)
    #TODO: use script info here to update node w/ proper info
    #set installer directory and last push directory depending on it (???)

    ########
    #starting_directory.git.checkout(active_branch)

    #starting_directory.remotes.origin.pull()
    ########

    #####TODO: use index @ -1 to find the last element of a list


    #set source directory and installer directory
    #active_branch is devel or master
    #replace old node references to past versions/release/etc to updated ones
    #use md5 to make sure the right thing is being downloaded

    pass

def esgf_upload():
    #use rsync to upload
    pass

def stream_subprocess_output(command_string, file_handle):
    ''' Print out the stdout of the subprocess in real time '''
    process = subprocess.Popen(shlex.split(command_string), stdout=subprocess.PIPE)
    with process.stdout:
        for line in iter(process.stdout.readline, b''):
            print line,
            file_handle.write(line)
    # wait for the subprocess to exit
    process.wait()

def mkdir_p(path, mode=0777):
    '''Makes directory, passes if directory already exists'''
    try:
        os.makedirs(path, mode)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            print "{path} already exists".format(path=path)
            pass
        else:
            raise

def main():
    '''User prompted for build specifications '''
    build_list = []
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
        starting_directory = raw_input("Please provide the path to the"
                                       " repositories on your system: ").strip()
        if os.path.isdir(os.path.realpath(starting_directory)):
            starting_directory = os.path.realpath(starting_directory)
            break
        else:
            create_path_q = raw_input("The path does not exist. Do you want "
                                      + starting_directory
                                      + " to be created? (Y or YES)")
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
    #list a menu to select repos to build
    print repo_info.REPO_MENU
    while True:
        #user selects what repos they want built
        select_repo = raw_input("Which repositories will be built? (Hit [Enter] for all) ")
        #if the user does not enter anything, ask about build all
        if not select_repo:
            all_repo_q = raw_input("Do you want to build all repositories? (Y or YES) ")
            #if they do not say yes, ask them again which repos will be built
            if all_repo_q.lower() not in ["yes", "y"]:
                print "Not a valid response."
                continue
            #if they do say yes then the build list is all the repos
            else:
                build_list = repo_info.REPO_LIST
                break
        #if the user does enter something, convert to list of ints
        else:
            try:
                select_repo = select_repo.split(',')
                select_repo = map(int, select_repo)
                try:
                    for repo in select_repo:
                        #append the menu items based on the number selected
                        build_list.append(repo_info.REPO_LIST[repo])
                    break
                #if append fails then a value not in index
                except IndexError:
                    print "Invalid entry, please enter repos to build."
                    continue
            #if mapping fails, then an incorrect value must have been entered
            except ValueError:
                print "Invalid entry, please enter repos to build."
                continue
    build_all(build_list, starting_directory)

    #Use a raw_input statement to ask the user to set the script_major_version, script_release, and
    #script_version
    #print the
    #TODO: develop an option to go back to using default settings
    print ("Default Script Settings: \n"
           + 'SCRIPT_MAJOR_VERSION = ' + repo_info.SCRIPT_MAJOR_VERSION + "\n"
           + 'SCRIPT_RELEASE = ' + repo_info.SCRIPT_RELEASE + "\n"
           + 'SCRIPT_VERSION = ' + repo_info.SCRIPT_VERSION)

    default_script_q = raw_input("\nDo you want to use the default script settings? (Y or YES): ")
    if default_script_q.lower() not in ['y', 'yes', '\n']:
        script_major_version = raw_input("Please set the script_major_version: ")
        script_release = raw_input("Please set the script_release: ")
        script_version = raw_input("Please set the script version: ")
    else:
        print "Using default script settings."
        script_major_version = repo_info.SCRIPT_MAJOR_VERSION
        script_release = repo_info.SCRIPT_RELEASE
        script_version = repo_info.SCRIPT_VERSION

    print "Script settings set.\n"
    #execute the create_esgf_tarballs() function
    create_esgf_tarballs(starting_directory, build_list)

    #execute the create_local_mirror_directory(active_branch), passing in
    #active_branch as an argument
    create_local_mirror_directory(active_branch, starting_directory)
    #execute update_esg_node(active_branch), passing in active_branch as an argument
    #update_esg_node(active_branch, starting_directory, script_major_version
    #                , script_release, script_version)
    #execute esgf_upload()

if __name__ == '__main__':
    main()
