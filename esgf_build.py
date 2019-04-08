#!usr/bin/env python
"""Modules needed mostly to access terminal commands."""
import os
import sys
import logging
from git import Repo
import repo_info
import build_utilities
import semver
import click
from github_release import gh_release_create, gh_asset_upload, get_releases, gh_release_edit, get_release_info
from git import RemoteProgress
from plumbum.commands import ProcessExecutionError
from plumbum import local
import re
from distutils.version import LooseVersion

logger = logging.basicConfig(level=logging.DEBUG,
                             format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("esgf_build")


###########################################
# Git Utility Functions

class ProgressPrinter(RemoteProgress):
    """Print the progress of cloning from GitHub on the command line."""

    def update(self, op_code, cur_count, max_count=None, message=''):
        """Print progress update message."""
        print op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE"


def list_remote_tags():
    """Return a list of the tags on the remote repo."""
    git = local['git']

    tags = git["ls-remote", "--tags", "origin"]()
    tags = str(tags)
    remote_tags = [re.sub(r"^\W+|\W+$", '', x.rsplit("/")[-1]) for x in tags.split("\n") if x]
    remote_tags = sorted(set(remote_tags), key=LooseVersion, reverse=True)
    return remote_tags


def list_local_tags(repo):
    """Return a list of the tags on the local repo."""
    # A tag can point to a blob and the loop prunes blob tags from the list of tags to be sorted
    tag_list = []
    for bar in repo.tags:
        try:
            bar.commit.committed_datetime
        except ValueError:
            pass
        else:
            tag_list.append(bar)
    local_tags = [str(tag) for tag in sorted(tag_list, key=lambda t: t.commit.committed_datetime)]
    return local_tags


def update_tags(repo):
    """Update tags on the repo."""
    build_utilities.call_binary("git", ["fetch", "--tags"])
    remote_tags = set(list_remote_tags())
    local_tags = set(list_local_tags(repo))

    local_only_tags = local_tags.difference(remote_tags)

    if local_only_tags:
        print "The following tags only exist locally and are not in sync with remote: {}".format(", ".join(local_only_tags))
        delete_local_tags = raw_input("Would you like to delete them? [Y/n]: ") or "yes"
        if delete_local_tags.lower() in ["y", "yes"]:
            for tag in local_only_tags:
                build_utilities.call_binary("git", ["tag", "-d", tag])


def get_latest_tag(repo):
    """Accept a GitPython Repo object and returns the latest annotated tag.

    Provides all the tags, reverses them (so that you can get the latest
    tag) and then takes only the first from the list.
    """
    sorted_tags = list_local_tags(repo)
    latest_tag = str(sorted_tags[-1])
    print "latest tag found:", latest_tag
    return latest_tag


def update_repo(repo_name, repo_object):
    """Accept a GitPython Repo object and updates the specified branch."""
    update_tags(repo_object)

    progress_printer = ProgressPrinter()
    print "Pulling latest updates for {repo_name} from GitHub".format(repo_name=repo_name)
    repo_object.remotes.origin.fetch(progress=progress_printer)


def clone_repo(repo, repo_directory):
    """Clone a repository from GitHub."""
    repo_path = os.path.join(repo_directory, repo)
    print "Cloning {} repo from Github".format(repo)
    Repo.clone_from(repo_info.ALL_REPO_URLS[repo], repo_path,
                    progress=ProgressPrinter())
    print(repo + " successfully cloned -> {repo_path}".format(repo_path=repo_path))


def list_branches(repo_handle):
    """List all branches for a repo."""
    repo_handle.remotes[0].fetch()
    remote_branches = [str(remote_branch.split("/")[1]) for remote_branch in repo_handle.git.branch('-r').split() if "origin" in remote_branch]
    local_branches = [repo.name for repo in repo_handle.branches]
    all_branches = set().union(remote_branches, local_branches)
    return all_branches


def update_all(repo_directory, repo):
    """Check each repo in the REPO_LIST for the most updated branch, and uses taglist to track versions."""
    print "Beginning to update directories."

    try:
        os.chdir(repo_directory + "/" + repo)
    except OSError:
        print "Directory for {repo} does not exist".format(repo=repo)
        clone_repo(repo, repo_directory)
        os.chdir(repo_directory + "/" + repo)

    repo_handle = Repo(os.getcwd())

    print "Updating {}".format(repo)
    update_repo(repo, repo_handle)

    os.chdir("..")
    print "Directory updates complete."


###########################################
# Ant Utility Functions


def clean(repo, log_directory, clean_command="clean_all"):
    """Run the clean directive from a repo's build script."""
    clean_log = os.path.join(log_directory, repo + "-clean.log")
    with open(clean_log, "w") as clean_log_file:
        clean_output = build_utilities.call_binary("ant", [clean_command])
        clean_log_file.write(clean_output)


def pull(repo, log_directory, pull_command="pull"):
    """Run the pull directive from a repo's build script."""
    pull_log = log_directory + "/" + repo + "-pull.log"
    with open(pull_log, "w") as pull_log_file:
        pull_output = build_utilities.call_binary("ant", [pull_command])
        pull_log_file.write(pull_output)


def build(repo, log_directory, build_command="make_dist"):
    """Run the build directive from a repo's build script."""
    build_log = os.path.join(log_directory, repo + "-build.log")

    with open(build_log, "w") as build_log_file:
        build_output = build_utilities.call_binary("ant", [build_command])
        build_log_file.write(build_output)


def publish_local(repo, log_directory, publish_command="publish_local"):
    """Run the publish local directive from a repo's build script."""
    publish_local_log = log_directory + "/" + repo + "-publishlocal.log"
    with open(publish_local_log, "w") as publish_local_log_file:
        publish_local_output = build_utilities.call_binary("ant", [publish_command])
        publish_local_log_file.write(publish_local_output)


def build_all(build_source, repo, starting_directory):
    """Take a list of repositories to build, and uses ant to build them."""
    log_directory = starting_directory + "/buildlogs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    print "Building repo: " + repo
    os.chdir(starting_directory + "/" + repo)
    logger.info(os.getcwd())
    if build_source[0] == "tag":
        print "Building from tag {}".format(build_source[1])
        try:
            build_utilities.call_binary("git", ["checkout", "tags/{}".format(build_source[1])])
        except ProcessExecutionError, error:
            logger.error(error)
            logger.error("No tag with name %s found. Exiting", build_source[1])

        print "sanity check:", build_utilities.call_binary("git", ["describe"])
    elif build_source[0] == "branch":
        print "Building from branch {}".format(build_source[1])
        try:
            build_utilities.call_binary("git", ["checkout", build_source[1]])
        except ProcessExecutionError, error:
            logger.error(error)
            if error.retcode == 1:
                logger.error("No branch with name %s found. Exiting", build_source[1])
            sys.exit(1)
        else:
            build_utilities.call_binary("git", ["pull"])
            print "sanity check branch:", build_utilities.call_binary("git", ["rev-parse", "--abbrev-ref", "HEAD"])

    else:
        print "No branch or tag was selected as the build source. Exiting."
        sys.exit(1)

    # repos getcert and stats-api do not need an ant pull call
    if repo == 'esgf-getcert':
        # clean and dist only
        clean(repo, log_directory, clean_command="clean")
        build(repo, log_directory, build_command="dist")
        os.chdir("..")
        # continue

    elif repo == 'esgf-stats-api':
        # clean and make_dist only
        clean(repo, log_directory)
        build(repo, log_directory)
        os.chdir('..')
        # continue
    else:
        # clean, build, and make_dist, publish to local repo
        clean(repo, log_directory)
        pull(repo, log_directory)
        build(repo, log_directory)
        publish_local(repo, log_directory)
    os.chdir("..")

    print "\nRepository builds complete."


def query_for_upload():
    """Choose whether or not to upload assets to GitHub.

    Invokes when the upload command line option is not present.
    """
    while True:
        upload_assets = raw_input("Would you like to upload the built assets to GitHub? [Y/n]") or "yes"
        if upload_assets.lower() in ["y", "yes"]:
            upload = True
            break
        elif upload_assets.lower() in ["n", "no"]:
            upload = False
            break
        else:
            print "Please choose a valid option"
    return upload


def get_published_releases(repo_name):
    """Return the versions of the releases that have been published to GitHub."""
    published_releases = [release["name"] for release in get_releases(repo_name)]
    print "published_releases:", published_releases
    return published_releases


def is_prerelease(repo_name, tag):
    release_info = get_release_info(repo_name, tag)
    return release_info["prerelease"]


def esgf_upload(starting_directory, repo, name, upload_flag=False, prerelease_flag=False, dryrun=False):
    """Upload binaries to GitHub release as assets."""
    if upload_flag is None:
        upload_flag = query_for_upload()

    if not upload_flag:
        return

    if prerelease_flag:
        print "Marking as prerelease"

    print "repo:", repo
    os.chdir(os.path.join(starting_directory, repo))
    repo_handle = Repo(os.getcwd())
    try:
        print "active branch before upload:", repo_handle.active_branch
    except TypeError, error:
        logger.debug(error)

    latest_tag = get_latest_tag(repo_handle)
    print "latest_tag:", latest_tag

    if not name:
        release_name = latest_tag
    else:
        release_name = name

    published_releases = get_published_releases("ESGF/{}".format(repo))

    if latest_tag in published_releases:
        if not prerelease_flag:
            print "removing prerelease label"
            gh_release_edit("ESGF/{}".format(repo), latest_tag, prerelease=False)
            if is_prerelease("ESGF/{}".format(repo), latest_tag):
                raise RuntimeError("Prerelease flag not removed")
        print "Updating the assets for the latest tag {}".format(latest_tag)
        gh_asset_upload("ESGF/{}".format(repo), latest_tag, "{}/{}/dist/*".format(starting_directory, repo), dry_run=dryrun, verbose=False)
    else:
        print "Creating release version {} for {}".format(latest_tag, repo)
        gh_release_create("ESGF/{}".format(repo), "{}".format(latest_tag), publish=True, name=release_name, prerelease=prerelease_flag, dry_run=dryrun, asset_pattern="{}/{}/dist/*".format(starting_directory, repo))

    print "Upload completed!"


def create_build_list(select_repo):
    """Create a list of repos to build depending on a menu that the user picks from."""
    # If the user has selcted the repos to build, the indexes are used to select
    # the repo names from the menu and they are appended to the build_list
    select_repo_list = select_repo.split(',')
    print "select_repo_list:", select_repo_list
    select_repo_map = map(int, select_repo_list)
    print "select_repo_map:", select_repo_map

    build_list = []
    for repo_num in select_repo_map:
        repo_name = repo_info.REPO_LIST[repo_num]
        build_list.append(repo_name)
    if not build_list:
        print "No applicable repos selected."
        exit()
    else:
        print "Building repos: " + str(build_list)
        print "\n"
        return build_list


def find_path_to_repos(starting_directory):
    """Check the path provided to the repos to see if it exists."""
    if os.path.isdir(os.path.realpath(starting_directory)):
        starting_directory = os.path.realpath(starting_directory)
        return True
    create_path_q = raw_input("The path does not exist. Do you want {} to be created? (Y or YES)".format(starting_directory)) or "y"
    if create_path_q.lower() not in ["yes", "y"]:
        print "Not a valid response. Directory not created."
        return False
    else:
        print "Creating directory {}".format(create_path_q)
        os.makedirs(starting_directory)
        starting_directory = os.path.realpath(starting_directory)
        return True


def choose_tag(starting_directory, repo):
    with build_utilities.pushd(os.path.join(starting_directory, repo)):
        tags = list_remote_tags()
        print "\n".join(tags)
        while True:
            tag_choice = raw_input("Enter the tag name:")
            if tag_choice not in tags:
                print "The tag {} does not exist for repo {}".format(tag_choice, repo)
                print "Please choose a valid tag."
                continue
            else:
                return ("tag", tag_choice)
                break


def choose_branch(starting_directory, repo):
    """Choose a git branch or tag name to checkout and build."""
    repo_handle = Repo(os.path.join(starting_directory, repo))
    branches = list_branches(repo_handle)
    while True:
        print "Available branches: ", branches
        active_branch = raw_input("Enter a branch name to checkout for the build. You can also enter 'latest' to build from the latest tag: ")

        if active_branch.lower() not in branches and active_branch.lower() not in ["latest"]:
            print "{} is not a valid branch.".format(active_branch)
            print "Please choose either a valid branch from the list or 'latest' for the most recent tag."
            continue
        else:
            break
    return ("branch", active_branch)


def choose_directory():
    """Choose the absolute path where the ESGF repos are located on your system.

    If the repos do not currently exist in the given directory, they will be cloned into the directory.
    """
    while True:
        starting_directory = raw_input("Please provide the path to the repositories on your system: ").strip()
        if find_path_to_repos(starting_directory):
            break
    return starting_directory


def choose_repos():
    """Display a menu for a user to choose repos to be built.

    Use a raw_input statement to ask which repos should be built, then call
    the create_build_list.
    """
    print repo_info.REPO_MENU
    while True:
        select_repo = raw_input("Which repository will be built? ")
        if not select_repo:
            print "Not a valid response."
            continue
        else:
            try:
                build_list = create_build_list(select_repo)
                break
            except (ValueError, IndexError), error:
                logger.error(error)
                print "Invalid entry, please enter repos to build."
                continue
    return build_list


def check_java_compiler():
    """Check if a suitable Java compiler is found.

    The ESGF webapps currently support being built with Java 8 (JRE class number 52).
    An exception will be raised if an incompatible Java compiler is found.
    """
    javac = build_utilities.call_binary("javac", ["-version"], stderr_output=True)
    javac = javac.split(" ")[1]
    if not javac.startswith("1.8.0"):
        raise EnvironmentError("Your Java compiler must be a Java 8 compiler (JRE class number 52). Java compiler version {} was found using javac -version".format(javac))


@click.command()
@click.option('--branch', '-b', default=None, help='Name of the git branch to checkout and build. Mutually exclusive with the --tag option.')
@click.option('--tag', '-t', default=None, help='Name of the git tag to checkout and build. Mutually exclusive with the --branch option.')
@click.option('--directory', '-d', default=None, help="Directory where the ESGF repos are located on your system")
@click.option('--name', '-n', default=None, help="Name of the release")
@click.option('--upload/--no-upload', is_flag=True, default=None, help="Upload built assets to GitHub")
@click.option('--prerelease', '-p', is_flag=True, help="Tag release as prerelease")
@click.option('--dryrun', '-r', is_flag=True, help="Perform a dry run of the release")
@click.argument('repos', default=None, nargs=1, type=click.Choice(['esgf-dashboard', 'esgf-getcert', 'esgf-idp', 'esgf-node-manager', 'esgf-security', 'esg-orp', 'esg-search', 'esgf-stats-api']))
def main(branch, tag, directory, repos, upload, prerelease, dryrun, name):
    """User prompted for build specifications and functions for build are called."""
    print "upload:", upload
    print "prerelease:", prerelease
    print "directory:", directory
    print "repos:", repos

    if repos:
        build_list = repos
    else:
        build_list = choose_repos()

    print "build_list:", build_list

    if not directory:
        starting_directory = choose_directory()
    else:
        if find_path_to_repos(directory):
            starting_directory = directory
        else:
            starting_directory = choose_directory()

    print "Using build directory {}".format(starting_directory)
    update_all(starting_directory, build_list)

    if branch and tag:
        print("Specifying a branch and a tag is invalid.  You must choose a branch OR a tag to build from.")
        sys.exit(1)

    if not branch and not tag:
        while True:
            build_choice = raw_input("Do you want to build from a branch or a tag? ")
            if build_choice.strip().lower() == "tag":
                build_source = choose_tag(starting_directory, repos)
                break
            elif build_choice.strip().lower() == "branch":
                build_source = choose_branch(starting_directory, repos)
                break
            else:
                print("Invalid option.  Please enter either 'branch' or 'tag'.")

    if branch:
        build_source = ("branch", branch)
    if tag:
        build_source = ("tag", tag)

    check_java_compiler()

    build_all(build_source, build_list, starting_directory)
    esgf_upload(starting_directory, build_list, name, upload, prerelease, dryrun)


if __name__ == '__main__':
    main()
