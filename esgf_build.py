#!usr/bin/env python
'''Modules needed mostly to access terminal commands'''
import subprocess
import shlex
import os
import shutil
import glob
from distutils.spawn import find_executable
import mmap
from git import Repo
import repo_info
import build_utilities
import datetime

######IMPORTANT################################################################
# Everything works and is tested up to update node and upload.
# Still need to try and eliminate tarballs entirely, eliminate hard-coded
# script settings in esg-node, use subprocess to set java and python paths,
# remove ivy.xml, etc.
#
# Current idea was to replace build_list with repo_info.CREATE_DIRECTORY_LIST
# in create_local_mirror_directory and create_esgf_tarballs function in order to
# set up esgf-installer which is needed in line 162 onward.
#
# esgf_upload remains un-tested and is a direct copy of the bash script
# into a subprocess.


from git import RemoteProgress


class ProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE"


def get_latest_tag(repo):
    '''accepts a GitPython Repo object and returns the latest annotated tag '''
    # provides all the tags, reverses them (so that you can get the latest
    # tag) and then takes only the first from the list
    tag_list = repo.tags
    latest_tag = str(tag_list[-1])
    return latest_tag


def create_taglist_file(taglist_file, repo_name, latest_tag):
    ''' Creates a file containing the latest tag for each repo '''
    taglist_file.write("-------------------------\n")
    taglist_file.write(repo_name + "\n")
    taglist_file.write("-------------------------\n")
    taglist_file.write(latest_tag + "\n")
    taglist_file.write("\n")


def create_commits_since_last_tag_file(commits_since_last_tag_file, repo_name, latest_tag):
    commits_since_tag = subprocess.check_output(shlex.split(
        "git log {latest_tag}..HEAD".format(latest_tag=latest_tag)))
    if commits_since_tag:
        print "There are new commits since the last annotated tag for {repo_name}".format(repo_name=repo_name)
        print "See commits_since_last_tag.txt for more details \n"
        commits_since_last_tag_file.write("-------------------------\n")
        commits_since_last_tag_file.write("Commits since last tag ({latest_tag}) for {repo_name}".format(
            latest_tag=latest_tag, repo_name=repo_name) + "\n")
        commits_since_last_tag_file.write("-------------------------\n")
        commits_since_last_tag_file.write(commits_since_tag + "\n")


def update_repo(repo_name, repo_object, active_branch):
    ''' accepts a GitPython Repo object and updates the specified branch '''
    print "Checkout {repo_name}'s {active_branch} branch".format(repo_name=repo_name, active_branch=active_branch)
    repo_object.git.checkout(active_branch)
    progress_printer = ProgressPrinter()
    repo_object.remotes.origin.pull("{active_branch}:{active_branch}".format(
        active_branch=active_branch), progress=progress_printer)
    print "Updating: " + repo_name


def update_all(active_branch, repo_directory):
    '''Checks each repo in the REPO_LIST for the most updated branch, and uses
    taglist to track versions '''
    print "Beginning to update directories."

    commits_since_last_tag_file = open(os.path.join(
        repo_directory, "commits_since_last_tag.txt"), "w")
    taglist_file = open(os.path.join(repo_directory, "taglist.txt"), "w+")
    for repo in repo_info.REPO_LIST:
        try:
            os.chdir(repo_directory + "/" + repo)
        except OSError:
            print "Directory for {repo} does not exist".format(repo=repo)

        repo_handle = Repo(os.getcwd())
        update_repo(repo, repo_handle, active_branch)

        latest_tag = get_latest_tag(repo_handle)
        create_taglist_file(taglist_file, repo, latest_tag)

        create_commits_since_last_tag_file(commits_since_last_tag_file, repo, latest_tag)

        os.chdir("..")

    taglist_file.close()
    commits_since_last_tag_file.close()
    print "Directory updates complete."


def build_all(build_list, starting_directory):
    '''Takes a list of repositories to build, and uses ant to build them '''
    # TODO: use subprocess w/ bash command to set the java and python paths
    # TODO: add loading bar while ant runs?
    # TODO: include installer in build script for final version
    # TODO: Remove ivy.xml directory?
    ant_path = find_executable('ant')
    #java_path = find_executable('java')
    #python_path = find_executable('python')

    log_directory = starting_directory + "/buildlogs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    for repo in build_list:
        print "Building repo: " + repo
        os.chdir(starting_directory + "/" + repo)

        # repos getcert and stats-api do not need an ant pull call
        if repo == 'esgf-getcert':
            #clean and dist only
            clean_log = log_directory + "/" + repo + "-clean.log"
            with open(clean_log, "w") as fgc1:
                build_utilities.stream_subprocess_output('{ant} clean'.format(ant=ant_path), fgc1)
            build_log = log_directory + "/" + repo + "-build.log"
            with open(build_log, "w") as fgc2:
                build_utilities.stream_subprocess_output('{ant} dist'.format(ant=ant_path), fgc2)
            os.chdir("..")
            continue

        if repo == 'esgf-stats-api':
            #clean and make_dist only
            clean_log = log_directory + "/" + repo + "-clean.log"
            with open(clean_log, "w") as fsapi1:
                build_utilities.stream_subprocess_output(
                    '{ant} clean_all'.format(ant=ant_path), fsapi1)
            build_log = log_directory + "/" + repo + "-build.log"
            with open(build_log, "w") as fsapi2:
                build_utilities.stream_subprocess_output(
                    "{ant} make_dist".format(ant=ant_path), fsapi2)
            os.chdir('..')
            continue

        #clean, build, and make_dist
        #TODO: Add publish step
        clean_log = log_directory + "/" + repo + "-clean.log"
        with open(clean_log, "w") as file1:
            build_utilities.stream_subprocess_output('{ant} clean_all'.format(ant=ant_path), file1)
        pull_log = log_directory + "/" + repo + "-pull.log"
        with open(pull_log, "w") as file2:
            build_utilities.stream_subprocess_output('{ant} pull'.format(ant=ant_path), file2)
        build_log = log_directory + "/" + repo + "-build.log"
        with open(build_log, "w") as file3:
            build_utilities.stream_subprocess_output("{ant} make_dist".format(ant=ant_path), file3)
        os.chdir("..")

    print "\nRepository builds complete."

    #TODO: extract to separate function
    #TODO: list clean, pull, and publish logs as well
    print "Finding esgf log files.\n"

    # uses glob to find all esgf log files then iterates over the log files ,
    # opens them and uses a mmap object to search through for BUILD reference
    # returns the ones with BUILD references to be checked by a script during build
    all_logs = glob.glob('buildlogs/esg*-*-build.log')
    for log in all_logs:
        with open(log) as flog:
            mmap_object = mmap.mmap(flog.fileno(), 0, access=mmap.ACCESS_READ)
            if mmap_object.find('BUILD') != -1:
                return log


def copy_artifacts_to_local_mirror(esgf_artifact_directory):
    ''' The web artifacts (jars and wars) get placed at
    ~/.ivy2/local/esgf-artifacts/ after running the ant builds. This function
    copies them to the local mirror'''
    local_artifacts_directory = os.path.join(os.environ["HOME"], ".ivy2", "local", "esgf-artifacts")
    try:
        shutil.copytree(local_artifacts_directory, esgf_artifact_directory)
    except OSError, error:
        shutil.rmtree(esgf_artifact_directory)
        shutil.copytree(local_artifacts_directory, esgf_artifact_directory)


def create_local_mirror_directory(active_branch, starting_directory, build_list, script_major_version):
    '''Creates a directory for ESGF binaries that will get RSynced and uploaded to the remote distribution mirrors'''
    # if active_branch is devel then copy to dist folder for devel
    # if active_branch is master then copy to dist folder
    print "\nCreating local mirrror directory."
    print "starting_directory:", starting_directory
    components = {}
    components["esgf-dashboard"] = ['bin/esg-dashboard',
                                    'dist/esgf_dashboard-0.0.0-py2.7.egg', 'INSTALL', 'README', 'LICENSE']
    components["esgf-idp"] = ['bin/esg-idp', 'INSTALL', 'README', 'LICENSE']
    components["esgf-installer"] = ['jar_security_scan', 'globus/esg-globus', 'esg-bootstrap', 'esg-node', 'esg-init', 'esg-functions', 'esg-gitstrap',
                                    'esg-node.completion', 'esg-purge.sh', 'compute-tools/esg-compute-languages', 'compute-tools/esg-compute-tools', 'INSTALL', 'README.md', 'LICENSE']
    components["esgf-node-manager"] = ['bin/esg-node-manager', 'bin/esgf-sh', 'bin/esgf-spotcheck',
                                       'etc/xsd/registration/registration.xsd', 'INSTALL', 'README', 'LICENSE']
    components["esgf-security"] = ['bin/esgf-user-migrate', 'bin/esg-security',
                                   'bin/esgf-policy-check', 'INSTALL', 'README', 'LICENSE']
    components["esg-orp"] = ['bin/esg-orp', 'INSTALL', 'README', 'LICENSE']
    # components['esgf-getcert'] = ['README', 'LICENSE']
    components["esg-search"] = ['bin/esg-search', 'bin/esgf-crawl', 'bin/esgf-optimize-index', 'etc/conf/jetty/jetty.xml-auth',
                                'etc/conf/jetty/realm.properties', 'etc/conf/jetty/webdefault.xml-auth', 'INSTALL', 'README', 'LICENSE']
    components['esgf-product-server'] = ['esg-product-server']
    components["filters"] = ['esg-access-logging-filter', 'esg-drs-resolving-filter',
                             'esg-security-las-ip-filter', 'esg-security-tokenless-filters']
    components["esgf-cog"] = ['esg-cog']
    # components['esgf-stats-api'] = ['bin/esg_stats-api_v2', 'dist/esgf-stats-api.war']

    # Make separate directories and move these components from esgf-installer to new specific directories
    try:
        shutil.copytree("esgf-installer/product-server/", "esgf-product-server")
    except OSError, error:
        shutil.rmtree("esgf-product-server")
        shutil.copytree("esgf-installer/product-server/", "esgf-product-server")

    try:
        shutil.copytree("esgf-installer/filters/", "filters")
    except OSError, error:
        shutil.rmtree("filters")
        shutil.copytree("esgf-installer/filters/", "filters")

    try:
        shutil.copytree("esgf-installer/cog/", "esgf-cog")
    except OSError, error:
        shutil.rmtree("esgf-cog")
        shutil.copytree("esgf-installer/cog/", "esgf-cog")

    # dist-repos -> esgf_bin
    if active_branch == "devel":
        esgf_binary_directory = os.path.join(
            starting_directory, 'esgf_bin', 'prod', 'dist', 'devel')
    else:
        esgf_binary_directory = os.path.join(starting_directory, 'esgf_bin', 'prod', 'dist')
    esgf_artifact_directory = os.path.join(starting_directory, 'esgf_bin', 'prod', 'artifacts')

    build_utilities.mkdir_p(esgf_binary_directory)
    build_utilities.mkdir_p(esgf_artifact_directory)

    copy_artifacts_to_local_mirror(esgf_artifact_directory)

    for component in components.keys():
        if component == "esgf-installer":
            component_binary_directory = os.path.join(esgf_binary_directory, component, script_major_version)
            print "esgf-installer binary directory:", component_binary_directory
        else:
            component_binary_directory = os.path.join(esgf_binary_directory, component)
        build_utilities.mkdir_p(component_binary_directory)
        os.chdir(component)
        print "current_directory: ", os.getcwd()
        for file_path in components[component]:
            shutil.copy(file_path, component_binary_directory)

        os.chdir("..")


def update_esg_node(active_branch, starting_directory, script_settings_local):
    '''Updates information in esg-node file'''
    # os.chdir("../esgf-installer")
    with build_utilities.pushd("../esgf-installer"):
        src_dir = os.getcwd()

        repo_handle = Repo(os.getcwd())
        repo_handle.git.checkout(active_branch)
        repo_handle.remotes.origin.pull()

        get_most_recent_commit(repo_handle)

        if active_branch == 'devel':
            installer_dir = os.path.join(starting_directory, 'esgf_bin', 'prod', 'dist', 'devel', 'esgf-installer', script_settings_local['script_major_version'])
            last_push_dir = os.path.join(starting_directory, 'esgf_bin', 'prod', 'dist', 'devel')
            build_utilities.mkdir_p(installer_dir)
        else:
            installer_dir = os.path.join(starting_directory, 'esgf_bin', 'prod', 'dist', 'esgf-installer', script_settings_local['script_major_version'])
            last_push_dir = os.path.join(starting_directory, 'esgf_bin', 'prod', 'dist')
            build_utilities.mkdir_p(installer_dir)

    replace_script_maj_version = '2.0'
    replace_release = 'Centaur'
    replace_version = 'v2.0-RC5.4.0-devel'

    print "Updating node with script versions."
    esg_node_path = os.path.join(installer_dir, 'esg-node')
    build_utilities.replace_string_in_file(esg_node_path, replace_script_maj_version,
                                           script_settings_local['script_major_version'])
    build_utilities.replace_string_in_file(
        esg_node_path, replace_release, script_settings_local['script_release'])
    build_utilities.replace_string_in_file(
        esg_node_path, replace_version, script_settings_local['script_version'])

    print "Copying esg-init and auto-installer."
    # shutil.copyfile(src_dir + "/esg-init", installer_dir + "/esg-init")
    # shutil.copyfile(src_dir + "/setup-autoinstall", installer_dir + "/setup-autoinstall")

    #Calculate md5sum checksums
    with build_utilities.pushd(installer_dir):
        with open('esg-init.md5', 'w') as file1:
            file1.write(build_utilities.get_md5sum('esg-init'))
        with open('esg-node.md5', 'w') as file1:
            file1.write(build_utilities.get_md5sum('esg-node'))
        # with open('esg-autoinstall.md5', 'w') as file1:
        #     file1.write(build_utilities.get_md5sum('esg-autoinstall'))

        with build_utilities.pushd(last_push_dir):
            with open('lastpush.md5', 'w') as file1:
                current_date = str(datetime.datetime.now())
                file1.write(build_utilities.get_md5sum(current_date))


def esgf_upload(starting_directory, dry_run=False):
    '''Uses rsync to upload to coffee server'''

    if dry_run:
        with open('esgfupload.log', 'a') as file1:
            build_utilities.stream_subprocess_output("rsync -arWvunO {dist_repos}/prod/ -e ssh --delete esgf@distrib-coffee.ipsl.jussieu.fr:/home/esgf/esgf/".format(dist_repos=os.path.join(starting_directory, 'esgf_bin')), file1)
    else:
        print "Beginning upload."
        with open('esgfupload.log', 'a') as file1:
            build_utilities.stream_subprocess_output("rsync -arWvu {dist_repos}/prod/ -e ssh --delete esgf@distrib-coffee.ipsl.jussieu.fr:/home/esgf/esgf/".format(dist_repos=os.path.join(starting_directory, 'esgf_bin')), file1)
        print "Upload completed!"


def create_build_list(build_list, select_repo, all_repos_opt):
    '''Creates a list of repos to build depending on a menu that the user picks from'''

    # If the user has indicated that all repos should be built, then the repos
    # from the repo list in repo info is purged of exclusions and set as the build_list
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

    # If the user has selcted the repos to build, the indexes are used to select
    # the repo names from the menu , any selected repos on the exclusion list are
    # purged, and the rest are appened to the build_list
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
                                                                  + " script_major_version: ")
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

    # Use a raw_input statement to ask which repos should be built, then call
    # the create_build_list with all_repos_opt set to either True or False
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

    # Ask the user if they want to use default script settings, if yes call the
    # set_script_settings function
    print ("Default Script Settings: \n"
           + 'SCRIPT_MAJOR_VERSION = ' + repo_info.SCRIPT_INFO['script_major_version'] + "\n"
           + 'SCRIPT_RELEASE = ' + repo_info.SCRIPT_INFO['script_release'] + "\n"
           + 'SCRIPT_VERSION = ' + repo_info.SCRIPT_INFO['script_version'])

    default_script_q = raw_input("\nDo you want to use the default script settings? (Y or YES): ")
    script_settings_local = set_script_settings(default_script_q, script_settings_local)
    print script_settings_local
    print "Script settings set."

    build_all(build_list, starting_directory)

    create_local_mirror_directory(active_branch, starting_directory, build_list, script_settings_local['script_major_version'])
    #
    try:
        update_esg_node(active_branch, starting_directory, script_settings_local)
    except IOError, error:
        print "error:", error
        print ("esgf_bin for installer not present, node update and server upload cannot be completed.")

    esgf_upload(starting_directory)


if __name__ == '__main__':
    main()
