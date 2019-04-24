from builder import esgf_build
from builder import build_utilities
from builder import purge_and_clone_fresh_repos
import os
import shutil
import pytest
from git import Repo


def finalizer_function():
    print "Deleting temp repos"
    shutil.rmtree("/tmp/esgf_repos")


@pytest.fixture(scope="session", autouse=True)
def setup_test_env(request):
    # prepare something ahead of all tests
    build_utilities.mkdir_p("/tmp/esgf_repos")
    with build_utilities.pushd("/tmp/esgf_repos/"):
        print "Cloning esgf-security"
        build_utilities.call_binary("git", ["clone", "https://github.com/ESGF/esgf-security.git"])
    # purge_and_clone_fresh_repos.main(os.path.join("tmp", "esgf_repos"))
    request.addfinalizer(finalizer_function)


def test_choose_directory():
    assert esgf_build.choose_directory("/Users/hill119/Development") == "/Users/hill119/Development"


def test_get_latest_tag():
    with build_utilities.pushd("/tmp/esgf_repos/esgf-security"):
        repo = Repo(os.getcwd())
        git_describe_output = build_utilities.call_binary("git", ["describe"])
        latest_tag = esgf_build.get_latest_tag(repo)
        assert latest_tag.strip() == git_describe_output.strip()


def test_list_remote_tags():
    with build_utilities.pushd("/tmp/esgf_repos/esgf-security"):
        assert esgf_build.list_remote_tags() is not []


def test_list_local_tags():
    with build_utilities.pushd("/tmp/esgf_repos/esgf-security"):
        repo = Repo(os.getcwd())
        assert esgf_build.list_local_tags(repo) is not []


def test_update_tags():
    with build_utilities.pushd("/tmp/esgf_repos/esgf-security"):
        repo = Repo(os.getcwd())
        git_describe_output = build_utilities.call_binary("git", ["describe"])
        remote_tags = esgf_build.list_remote_tags()
        print "remote_tags:", remote_tags
        print "git_describe_output:", git_describe_output
        # print "git describe:", build_utilities.call_binary("git", ["des])
        assert esgf_build.update_tags(repo) is True
        assert remote_tags[0].strip() == git_describe_output.strip()
