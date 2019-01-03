#!usr/bin/env python
"""Modules needed mostly to access terminal commands."""
import subprocess
import shlex
import os
import shutil
import logging
import glob
from distutils.spawn import find_executable
import mmap
from git import Repo
import repo_info
import build_utilities
import semver
from github_release import gh_release_create, gh_asset_upload, get_releases
from git import RemoteProgress
from plumbum.commands import ProcessExecutionError

logger = logging.basicConfig(level=logging.DEBUG,
                             format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("esgf_build")


class ProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE"


def get_latest_tag(repo):
    """Accept a GitPython Repo object and returns the latest annotated tag.

    Provides all the tags, reverses them (so that you can get the latest
    tag) and then takes only the first from the list.
    """
    # A tag can point to a blob and the loop prunes blob tags from the list of tags to be sorted
    tag_list = []
    for bar in repo.tags:
        try:
            bar.commit.committed_datetime
        except ValueError:
            pass
        else:
            tag_list.append(bar)
    sorted_tags = sorted(tag_list, key=lambda t: t.commit.committed_datetime)
    latest_tag = str(sorted_tags[-1])
    return latest_tag


def create_taglist_file(taglist_file, repo_name, latest_tag):
    """Create a file containing the latest tag for each repo."""
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
    """Accept a GitPython Repo object and updates the specified branch."""
    if active_branch == "latest":
        active_tag = get_latest_tag(repo_object)
        print "Checkout {repo_name}'s {active_tag} tag".format(repo_name=repo_name, active_tag=active_tag)
        try:
            build_utilities.call_binary("git", ["checkout", active_tag, "-b", active_tag])
        except ProcessExecutionError, err:
            if err.retcode == 128:
                pass
    else:
        print "Checkout {repo_name}'s {active_branch} branch".format(repo_name=repo_name, active_branch=active_branch)
        repo_object.git.checkout(active_branch)

        progress_printer = ProgressPrinter()
        repo_object.remotes.origin.pull("{active_branch}:{active_branch}".format(
            active_branch=active_branch), progress=progress_printer)
    print "Updating: " + repo_name


def clone_repo(repo, repo_directory):
    """Clone a repository from GitHub."""
    repo_path = os.path.join(repo_directory, repo)
    print "Cloning {} repo from Github".format(repo)
    Repo.clone_from(repo_info.ALL_REPO_URLS[repo], repo_path,
                    progress=ProgressPrinter())
    print(repo + " successfully cloned -> {repo_path}".format(repo_path=repo_path))


def update_all(active_branch, repo_directory, build_list):
    """Check each repo in the REPO_LIST for the most updated branch, and uses taglist to track versions."""
    print "Beginning to update directories."

    commits_since_last_tag_file = open(os.path.join(
        repo_directory, "commits_since_last_tag.txt"), "w")
    taglist_file = open(os.path.join(repo_directory, "taglist.txt"), "w+")

    for repo in build_list:
        try:
            os.chdir(repo_directory + "/" + repo)
        except OSError:
            print "Directory for {repo} does not exist".format(repo=repo)
            clone_repo(repo, repo_directory)
            os.chdir(repo_directory + "/" + repo)

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
    """Take a list of repositories to build, and uses ant to build them."""
    # TODO: Remove ivy.xml directory?
    ant_path = find_executable('ant')

    log_directory = starting_directory + "/buildlogs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    for repo in build_list:
        print "Building repo: " + repo
        os.chdir(starting_directory + "/" + repo)
        logger.info(os.getcwd())

        # repos getcert and stats-api do not need an ant pull call
        if repo == 'esgf-getcert':
            # clean and dist only
            clean_log = log_directory + "/" + repo + "-clean.log"
            with open(clean_log, "w") as fgc1:
                clean_output = build_utilities.call_binary("ant", ["clean"])
                fgc1.write(clean_output)

            build_log = log_directory + "/" + repo + "-build.log"

            with open(build_log, "w") as fgc2:
                build_output = build_utilities.call_binary("ant", ["dist"])
                fgc2.write(build_output)
            os.chdir("..")
            continue

        if repo == 'esgf-stats-api':
            # clean and make_dist only
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

        # clean, build, and make_dist
        # TODO: Add publish step
        clean_log = log_directory + "/" + repo + "-clean.log"
        with open(clean_log, "w") as file1:
            clean_all_output = build_utilities.call_binary("ant", ["clean_all"])
            file1.write(clean_all_output)
        pull_log = log_directory + "/" + repo + "-pull.log"
        with open(pull_log, "w") as file2:
            pull_output = build_utilities.call_binary("ant", ["pull"])
            file2.write(pull_output)
        build_log = log_directory + "/" + repo + "-build.log"
        with open(build_log, "w") as file3:
            make_dist_output = build_utilities.call_binary("ant", ["make_dist"])
            file3.write(make_dist_output)
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
    """The web artifacts (jars and wars) get placed at
    ~/.ivy2/local/esgf-artifacts/ after running the ant builds. This function
    copies them to the local mirror"""
    local_artifacts_directory = os.path.join(os.environ["HOME"], ".ivy2", "local", "esgf-artifacts")
    try:
        shutil.copytree(local_artifacts_directory, esgf_artifact_directory)
    except OSError, error:
        shutil.rmtree(esgf_artifact_directory)
        shutil.copytree(local_artifacts_directory, esgf_artifact_directory)


def create_local_mirror_directory(active_branch, starting_directory, build_list, script_major_version):
    """Create a directory for ESGF binaries that will get RSynced and uploaded to the remote distribution mirrors."""
    print "\nCreating local mirror directory."

    esgf_binary_directory = os.path.join(starting_directory, 'esgf_binaries')
    build_utilities.mkdir_p(esgf_binary_directory)
    build_utilities.mkdir_p(esgf_artifact_directory)

    copy_artifacts_to_local_mirror(esgf_artifact_directory)


def bump_tag_version(repo, current_version):
    """Use semver to bump the tag version."""
    print '----------------------------------------\n'
    print '0: Bump major version {} -> {} \n'.format(current_version, semver.bump_major(current_version))
    print '1: Bump minor version {} -> {} \n'.format(current_version, semver.bump_minor(current_version))
    print '2: Bump patch version {} -> {} \n'.format(current_version, semver.bump_patch(current_version))

    while True:
        selection = raw_input("Choose version number component to increment: ")
        if selection == "0":
            return semver.bump_major(current_version)
            break
        elif selection == "1":
            return semver.bump_minor(current_version)
            break
        elif selection == "2":
            return semver.bump_patch(current_version)
            break
        else:
            print "Invalid selection. Please make a valid selection."


def esgf_upload(starting_directory, build_list):
    """Upload binaries to GitHub release as assets."""
    while True:
        upload_assets = raw_input("Would you like to upload the binary assets to GitHub? [Y/n]: ") or "y"
        if upload_assets.lower() in ["n", "no"]:
            return
        elif upload_assets.lower() in ["y", "yes"]:
            print "attempting upload"
            break
        else:
            print "Please enter a valid selection."

    print "build list in upload:", build_list
    for repo in build_list:
        print "repo:", repo
        os.chdir(os.path.join(starting_directory, repo))
        repo_handle = Repo(os.getcwd())
        latest_tag = get_latest_tag(repo_handle)
        print "latest_tag:", latest_tag
        release_name = raw_input("Enter the title for this {} release: ".format(repo))
        bump_version = raw_input("Would you like to bump the version number of {} [Y/n]".format(repo)) or "yes"
        if bump_version.lower() in ["y", "yes"]:
            new_tag = bump_tag_version(repo, latest_tag)
            gh_release_create("ESGF/{}".format(repo), "{}".format(new_tag), publish=True, name=release_name, asset_pattern="{}/{}/dist/*".format(starting_directory, repo))
        else:
            print "get releases:"
            if latest_tag in get_releases("ESGF/{}".format(repo)):
                print "Updating the assets for the latest tag {}".format(latest_tag)
                gh_asset_upload("ESGF/{}".format(repo), latest_tag, "{}/{}/dist/*".format(starting_directory, repo), dry_run=False, verbose=False)
            else:
                print "Creating release version {} for {}".format(latest_tag, repo)
                gh_release_create("ESGF/{}".format(repo), "{}".format(latest_tag), publish=True, name=release_name, asset_pattern="{}/{}/dist/*".format(starting_directory, repo))

    print "Upload completed!"


def create_build_list(build_list, select_repo, all_repos_opt):
    """Creates a list of repos to build depending on a menu that the user picks from"""

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
    select_repo_list = select_repo.split(',')
    print "select_repo_list:", select_repo_list
    select_repo_map = map(int, select_repo_list)
    print "select_repo_map:", select_repo_map
    for repo_num in select_repo_map:
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


def find_path_to_repos(starting_directory):
    """Checks the path provided to the repos to see if it exists"""
    if os.path.isdir(os.path.realpath(starting_directory)):
        starting_directory = os.path.realpath(starting_directory)
        return True
    create_path_q = raw_input("The path does not exist. Do you want "
                              + starting_directory
                              + " to be created? (Y or YES)") or "y"
    if create_path_q.lower() not in ["yes", "y"]:
        print "Not a valid response. Directory not created."
        return False
    else:
        print "Creating directory {}".format(create_path_q)
        os.makedirs(starting_directory)
        starting_directory = os.path.realpath(starting_directory)
        return True


def get_most_recent_commit(repo_handle):
    """Gets the most recent commit w/ log and list comprehension"""
    repo_handle.git.log()
    mst_rcnt_cmmt = repo_handle.git.log().split("\ncommit")[0]
    return mst_rcnt_cmmt


def main():
    """User prompted for build specifications and functions for build are called."""
    build_list = []
    select_repo = []

    while True:
        active_branch = raw_input("Enter a branch name or tag name to checkout for the build. Valid options are 'devel' for the devel branch, 'master' for the master branch, or 'latest' for the latest tag: ")

        if active_branch.lower() not in ["devel", "master", "latest"]:
            print "Please choose either master, devel, or latest."
            continue
        else:
            break

    while True:
        starting_directory = raw_input("Please provide the path to the" +
                                       " repositories on your system: ").strip()
        if find_path_to_repos(starting_directory):
            break

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
            except (ValueError, IndexError), error:
                logger.error(error)
                print "Invalid entry, please enter repos to build."
                continue

    update_all(active_branch, starting_directory, build_list)
    build_all(build_list, starting_directory)
    esgf_upload(starting_directory, build_list)


if __name__ == '__main__':
    main()
