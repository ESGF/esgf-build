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
import hashlib
from git import Repo
import repo_info

######IMPORTANT################################################################
# Everything works and is tested up to update node and upload.
#Still need to try and eliminate tarballs entirely, eliminate hard-coded
#script settings in esg-node, use subprocess to set java and python paths,
#remove ivy.xml, etc.
#
# Current idea was to replace build_list with repo_info.CREATE_DIRECTORY_LIST
#in create_local_mirror_directory and create_esgf_tarballs function in order to
#set up esgf-installer which is needed in line 162 onward.
#
# esgf_upload remains un-tested and is a direct copy of the bash script
#into a subprocess.

def update_all(active_branch, starting_directory):
    '''Checks each repo in the REPO_LIST for the most updated branch, and uses
    taglist to track versions '''
    print "Beginning to update directories."
    fileobject = open("taglist", "w")
    for repo in repo_info.REPO_LIST:
        try:
            os.chdir(starting_directory + "/" + repo)
        except OSError:
            print "Directory does not exist"
        repo_handle = Repo(os.getcwd())
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
        os.chdir("..")
    fileobject.close()
    print "Directory updates complete."

def build_all(build_list, starting_directory):
    '''Takes a list of repositories to build, and uses ant to build them '''
    #TODO: use subprocess w/ bash command to set the java and python paths
    #TODO: add loading bar while ant runs?
    #TODO: include installer in build script for final version
    #TODO: Remove ivy.xml directory?
    ant_path = find_executable('ant')
    #java_path = find_executable('java')
    #python_path = find_executable('python')

    log_directory = starting_directory + "/buildlogs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    for repo in build_list:
        print "Building repo: " + repo
        os.chdir(starting_directory + "/" + repo)
        #repos getcert and stats-api do not need an ant pull call
        if repo == 'esgf-getcert':
            clean_log = log_directory + "/" + repo + "-clean.log"
            with open(clean_log, "w") as fgc1:
                stream_subprocess_output('{ant} clean'.format(ant=ant_path), fgc1)
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
            continue
        clean_log = log_directory + "/" + repo + "-clean.log"
        with open(clean_log, "w") as file1:
            stream_subprocess_output('{ant} clean_all'.format(ant=ant_path), file1)
        pull_log = log_directory + "/" + repo + "-pull.log"
        with open(pull_log, "w") as file2:
            stream_subprocess_output('{ant} pull'.format(ant=ant_path), file2)
        build_log = log_directory + "/" + repo + "-build.log"
        with open(build_log, "w") as file3:
            stream_subprocess_output("{ant} make_dist".format(ant=ant_path), file3)
        os.chdir("..")

    print "\nRepository builds complete."
    print "Finding esgf log files.\n"

    #uses glob to find all esgf log files then iterates over the log files ,
    #opens them and uses a mmap object to search through for BUILD reference
    #returns the ones with BUILD references to be checked by a script during build
    all_logs = glob.glob('buildlogs/esg*-*-build.log')
    for log in all_logs:
        with open(log) as flog:
            mmap_object = mmap.mmap(flog.fileno(), 0, access=mmap.ACCESS_READ)
            if mmap_object.find('BUILD') != -1:
                return log

def create_esgf_tarballs(starting_directory, build_list):
    '''create_esgf_tarballs using tarfile'''
    tarball_dir = starting_directory + "/esgf_tarballs"
    print "Attempting to remove old tarballs."
    try:
        shutil.rmtree(tarball_dir)
        print "Old tarballs removed, beginning to create tarballs.\n"
    except OSError:
        print "No old tarballs located, beginning to create tarballs.\n"
    os.makedirs(tarball_dir)
    for repo in build_list:
        #each tarball will have it's own directory in the main tarball directory
        local_tarball_dir = os.path.join(tarball_dir, repo)
        #the path to the repo to create a tar of
        repo_path = os.path.join(starting_directory, repo)
        repo_path = os.path.realpath(repo_path)
        #changing directory to that repo to tar it
        os.chdir(tarball_dir)
        with tarfile.open(local_tarball_dir + ".tgz", "w:gz") as tar:
            #tar.add("../" + repo)
            tar.add(repo_path, arcname=repo)
        print repo + " tarball created."
        os.chdir("..")

def create_local_mirror_directory(active_branch, starting_directory, build_list):
    '''Creates a directory for binaries and untars to it'''
    #import pdb; pdb.set_trace()
    #if active_branch is devel then copy to dist folder for devel
    #if active_branch is master then copy to dist folder
    #untar in dist and delete tarballs
    print "\nCreating local mirrror directory."
    #dist-repos -> esgf_bin
    mkdir_p('../esgf_bin')
    os.chdir('esgf_tarballs')
    #goes to each tarball listed in the tarballs directory
    for tarball in os.listdir(os.getcwd()):
        #this is used to name each repo in esgf_bin
        trgt_dir = tarball.split(".")[0]
        mkdir_p('esgf_bin/prod/dist/devel/{tgt_dir}'.format(tgt_dir=trgt_dir))
        mkdir_p('esgf_bin/prod/dist/{tgt_dir}'.format(tgt_dir=trgt_dir))
        tar = tarfile.open(tarball)
        if active_branch == 'devel':
            tar.extractall(path="../esgf_bin/prod/dist/devel/{tgt_dir}".format(tgt_dir=trgt_dir))
        else:
            tar.extractall(path="../esgf_bin/prod/dist/{tgt_dir}".format(tgt_dir=trgt_dir))
        tar.close()
    print "Tarballs extracted to directory.\n"

def update_esg_node(active_branch, starting_directory, script_settings_local):
    '''Updates information in esg-node file'''
    #TODO: in the future, remove hard-coded script settings from esgf-node
    os.chdir("../esgf-installer")
    src_dir = os.getcwd()

    repo_handle = Repo(os.getcwd())
    repo_handle.git.checkout(active_branch)
    repo_handle.remotes.origin.pull()

    get_most_recent_commit(repo_handle)

    if active_branch == 'devel':
        installer_dir = (starting_directory
                         +'/esgf_bin/prod/dist/devel/esgf-installer/'
                         + script_settings_local['script_major_version'])
        last_push_dir = (starting_directory + '/dist-repos/prod/dist/devel')
    else:
        installer_dir = (starting_directory
                         + '/esgf_bin/prod/dist/esgf-installer/'
                         + script_settings_local['script_major_version'])
        last_push_dir = (starting_directory + '/dist-repos/prod/dist')

    replace_script_maj_version = '2.0'
    replace_release = 'Centaur'
    replace_version = 'v2.0-RC5.4.0-devel'

    print "Updating node with script versions."
    replace_string_in_file('esg-node', replace_script_maj_version,
                           script_settings_local['script_major_version'])
    replace_string_in_file('esg-node', replace_release, script_settings_local['script_release'])
    replace_string_in_file('esg-node', replace_version, script_settings_local['script_version'])

    print "Copying esg-init and auto-installer."
    shutil.copyfile(src_dir + "/esg-init", installer_dir + "/esg-init")
    shutil.copyfile(src_dir + "/setup-autoinstall", installer_dir + "/setup-autoinstall")

    with open('esg-init.md5', 'w') as file1:
        file1.write(get_md5sum('esg-init'))
    with open('esg-node.md5', 'w') as file1:
        file1.write(get_md5sum('esg-node'))
    with open('esg-autoinstall.md5', 'w') as file1:
        file1.write(get_md5sum('esg-autoinstall'))
    os.chdir(last_push_dir)
    with open('lastpush.md5', 'w') as file1:
        file1.write(get_md5sum(last_push_dir))

def esgf_upload():
    '''Uses rsync to upload to coffee server'''
    #use rsync to upload
    print "Beginning upload."
    with open('esgfupload.log', 'a') as file1:
        stream_subprocess_output("rsync -arWvu dist-repos/prod/ -e ssh --delete"
                                 /" esgf@distrib-coffee.ipsl.jussieu.fr:/home/esgf/esgf/"
                                 /"2>&1 |tee esgfupload.log", file1)
    with open('esgfupload.log', 'a') as file1:
        stream_subprocess_output("rsync -arWvunO dist-repos/prod/ -e ssh --delete"
                                 /"esgf@distrib-coffee.ipsl.jussieu.fr:/home/esgf/esgf/"
                                 /" 2>&1 |tee esgfupload.log", file1)
    print "Upload completed!"

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
            print "Removing and rebuilding path."
            shutil.rmtree(path)
            mkdir_p(path, mode=0777)
        else:
            raise

def replace_string_in_file(file_name, original_string, new_string):
    '''Goes into a file and replaces string'''
    with open(file_name, 'r') as file_handle:
        filedata = file_handle.read()
    filedata = filedata.replace(original_string, new_string)

    # Write the file out again
    with open(file_name, 'w') as file_handle:
        file_handle.write(filedata)

def create_build_list(build_list, select_repo, all_repos_opt):
    '''Creates a list of repos to build depending on a menu that the user picks from'''

    #If the user has indicated that all repos should be built, then the repos
    #from the repo list in repo info is purged of exclusions and set as the build_list
    if all_repos_opt is True:
        build_list = repo_info.REPO_LIST
        for repo in build_list:
            if repo in repo_info.REPOS_TO_EXCLUDE:
                print "EXCLUSION FOUND: " + repo
                build_list.remove(repo)
                continue
        print "Building repos: " + str(build_list)
        print "\n"
        return

    #If the user has selcted the repos to build, the indexes are used to select
    #the repo names from the menu , any selected repos on the exclusion list are
    #purged, and the rest are appened to the build_list
    select_repo = select_repo.split(',')
    select_repo = map(int, select_repo)
    for repo_num in select_repo:
        repo_name = repo_info.REPO_LIST[repo_num]

        if repo_name in repo_info.REPOS_TO_EXCLUDE:
            print "EXCLUSION FOUND: " + repo_name
            continue
        else:
            build_list.append(repo_name)
    if not build_list:
        print "No applicable repos selected."
        exit()
    else:
        print "Building repos: " + str(build_list)
        print "\n"

def set_script_settings(default_script_q, script_settings_local):
    '''Sets the script settings depending on input or default'''
    if default_script_q.lower() not in ['y', 'yes', '']:
        script_settings_local['script_major_version'] = raw_input("Please set the"
                                                                  +" script_major_version: ")
        script_settings_local['script_release'] = raw_input("Please set the script_release: ")
        script_settings_local['script_version'] = raw_input("Please set the script version: ")
        return script_settings_local
    print "Using default script settings."
    return repo_info.SCRIPT_INFO.copy()

def find_path_to_repos(starting_directory):
    '''Checks the path provided to the repos to see if it exists'''
    if os.path.isdir(os.path.realpath(starting_directory)):
        starting_directory = os.path.realpath(starting_directory)
        return False
    create_path_q = raw_input("The path does not exist. Do you want "
                              + starting_directory
                              + " to be created? (Y or YES)")
    if create_path_q.lower() not in ["yes", "y"]:
        print "Not a valid response. Directory not created."
        return True
    os.makedirs(starting_directory)
    starting_directory = os.path.realpath(starting_directory)
    return False

def get_most_recent_commit(repo_handle):
    '''Gets the most recent commit w/ log and list comprehension'''
    repo_handle.git.log()
    mst_rcnt_cmmt = repo_handle.git.log().split("\ncommit")[0]
    return mst_rcnt_cmmt

def get_md5sum(file_name):
    '''
        #Utility function, wraps md5sum so it may be used on either mac or
        #linux machines
    '''
    hasher = hashlib.md5()
    with open(file_name, 'rb') as file_handle:
        buf = file_handle.read()
        hasher.update(buf)
        file_name_md5 = hasher.hexdigest()
    return file_name_md5

def main():
    '''User prompted for build specifications and functions for build are called'''
    build_list = []
    select_repo = []
    script_settings_local = {}

    while True:
        active_branch = raw_input("Do you want to update devel or master branch? ")

        if active_branch.lower() not in ["devel", "master"]:
            print "Please choose either master or devel."
            continue
        else:
            break

    while True:
        starting_directory = raw_input("Please provide the path to the" +
                                       " repositories on your system: ").strip()
        if not find_path_to_repos(starting_directory):
            break

    update_all(active_branch, starting_directory)

    #Use a raw_input statement to ask which repos should be built, then call
    #the create_build_list with all_repos_opt set to either True or False
    print repo_info.REPO_MENU
    while True:
        select_repo = raw_input("Which repositories will be built? (Hit [Enter] for all) ")
        if not select_repo:
            all_repo_q = raw_input("Do you want to build all repositories? (Y or YES) ")
            if all_repo_q.lower() not in ["yes", "y", ""]:
                print "Not a valid response."
                continue
            else:
                create_build_list(build_list, select_repo, all_repos_opt=True)
                break
        else:
            try:
                create_build_list(build_list, select_repo, all_repos_opt=False)
                break
            except (ValueError, IndexError):
                print "Invalid entry, please enter repos to build."
                continue

    #Ask the user if they want to use default script settings, if yes call the
    #set_script_settings function
    print ("Default Script Settings: \n"
           + 'SCRIPT_MAJOR_VERSION = ' + repo_info.SCRIPT_INFO['script_major_version'] + "\n"
           + 'SCRIPT_RELEASE = ' + repo_info.SCRIPT_INFO['script_release'] + "\n"
           + 'SCRIPT_VERSION = ' + repo_info.SCRIPT_INFO['script_version'])

    default_script_q = raw_input("\nDo you want to use the default script settings? (Y or YES): ")
    script_settings_local = set_script_settings(default_script_q, script_settings_local)
    print script_settings_local
    print "Script settings set."

    build_all(build_list, starting_directory)

    create_esgf_tarballs(starting_directory, build_list)

    create_local_mirror_directory(active_branch, starting_directory, build_list)

    try:
        update_esg_node(active_branch, starting_directory, script_settings_local)
    except IOError:
        print ("esgf_bin for installer not present, node update and server upload cannot be completed.")

    #esgf_upload()

if __name__ == '__main__':
    main()
