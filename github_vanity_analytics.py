'''
Testing script
'''
import datetime
import logging
import pprint
import re
import requests

GIT_HUB_HOST = "https://api.github.com"


def list_github_repositories(username=None, organization=None, auth=None, **kwargs):
    """
    Get repositories owned by a user or an organization.
        - One of user or organization must be specified
    :param username: <string>
    :param organization: <string>
    :param auth: <tuple> (user, password)
    :param kwargs: <dict> Arguments to be passed to the api call
        https://developer.github.com/v3/repos/#list-your-repositories
    :return: <list> results   
    """
    if username:
        url_root = "{host}/users/{username}".format(host=GIT_HUB_HOST, username=username)
    elif not username and organization:
        url_root = "{host}/orgs/{organization}".format(host=GIT_HUB_HOST, organization=organization)
    else:
        raise ValueError("One (and only one) of username or organization parameters "
                         "must be specified")

    url = "{url_root}/repos".format(url_root=url_root)
    response = requests.get(url, params=kwargs, auth=auth)
    return response.json()


class GitHubVanityAnalytics(object):
    """
    Object used to interact with GitHub
    """
    def __init__(self, owner, repo, user, pwd):
        """
        Create the object and set the preferences
        :param owner: <string>
        :param repo: <string>
        :param user: <string>
        :param pwd: <string>
        """
        self.owner = owner
        self.repo = repo
        self.auth = (user, pwd)

    def get_contents(self, path, ref=None):
        """
        Get the contents of a path.
        :param path: <string> Path to list contents of
        :param ref: <string> The name of the commit/branch/tag. Default: repository's default branch
        :return: <list> results 
        """
        url = "{host}/repos/{owner}/{repo}/contents/{path}".format(
            host=GIT_HUB_HOST, owner=self.owner, repo=self.repo, path=path)
        response = requests.get(url, params={"ref": ref}, auth=self.auth)
        return response.json()

    def get_rate_limits(self):
        """
        Get the contents of a path.
        :param path: <string> Path to list contents of
        :param ref: <string> The name of the commit/branch/tag. Default: repository's default branch
        :return: <list> results 
        """
        response = requests.get("{host}/rate_limit".format(host=GIT_HUB_HOST), auth=self.auth)
        return response.json()

    # pylint: disable=R0913
    # R0913: Too many arguments
    def search_for_file(self, regex, path, recursive=False, ref=None, file_type=None):
        """
        Search for file.
        :param regex: <string> Regex to search for
        :param path: <string> Path to list contents of
        :param recursive: <bool> Recursively search through directories
        :param ref: <string> The name of the commit/branch/tag. Default: repository's default branch
        :param type: <string> file or dir. If None, searches for both
        :return: <list> Of files matching regex. 
        """
        matching_files = []
        contents = self.get_contents(path, ref)
        for listing in contents:
            if re.search(regex, listing["name"]) and (
                    file_type == None or listing["type"] == file_type):
                matching_files.append(listing)
            if recursive and listing["type"] == "dir":
                matching_files += self.search_for_file(
                    regex, listing["path"], recursive, ref, file_type)
        return matching_files

    def get_commits(self, **kwargs):
        """
        Get commits made to a repository.
        :param kwargs: <dict> Arguments to be passed to the api call
            See https://developer.github.com/v3/repos/commits/#list-commits-on-a-repository
        :return: <list> results   
        """
        url = "{host}/repos/{owner}/{repo}/commits".format(
            host=GIT_HUB_HOST, owner=self.owner, repo=self.repo)
        response = requests.get(url, params=kwargs, auth=self.auth)
        return response.json()

    def get_commit(self, sha, **kwargs):
        """
        Get commits made to a repository.
        :param sha: <string>
        :param kwargs: <dict> Arguments to be passed to the api call
            See https://developer.github.com/v3/repos/commits/
        :return: <list> results   
        """
        url = "{host}/repos/{owner}/{repo}/commits/{sha}".format(
            host=GIT_HUB_HOST, owner=self.owner, repo=self.repo, sha=sha)
        response = requests.get(url, params=kwargs, auth=self.auth)
        return response.json()

    def get_commit_stats(self, sha, stats_to_add=None, **kwargs):
        """
        Get commit stats (# of changes, additions, & deletions) grouped by owner
        :param sha: <string>
        :param stats_to_add: <dict> Stats that should be added to
        :param kwargs: <dict> Arguments to be passed to the api call
            See https://developer.github.com/v3/repos/commits/
        :return: <dict> keys are: files, additions, deletions, changes, committer
        """
        response = self.get_commit(sha, **kwargs)
        committer = None
        if not stats_to_add:
            stats_to_add = {}
        
        if response:
            if "author" in response and response["author"]:
                if "login" in response["author"]:
                    committer = response["author"]["login"]

        if committer:
            if not committer in stats_to_add:
                stats_to_add[committer] = {
                    "files": 0,
                    "additions": 0,
                    "deletions": 0,
                    "changes": 0,
                    "commits": 0,
                } 

            stats_to_add[committer]["commits"] += 1

            for gfile in response["files"]:
                stats_to_add[committer]["files"] += 1
                stats_to_add[committer]["additions"] += gfile["additions"]
                stats_to_add[committer]["changes"] += gfile["changes"]
                stats_to_add[committer]["deletions"] += gfile["deletions"]
        else:
            logging.debug("No committer or login found for sha: %s -- kwargs: %s",
                          sha, kwargs)

        return stats_to_add

def main():
    """
    Main program
    """
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', type=str, required=True)
    parser.add_argument('-p', '--password', type=str, required=True)
    parser.add_argument('-s', '--search_regex', type=str, required=True)

    parser.add_argument('-r', '--repositories', nargs='+', type=str)
    parser.add_argument('-o', '--organization', type=str)

    parsed_args = parser.parse_args()
    user = getattr(parsed_args, "user")
    password = getattr(parsed_args, "password")
    regex = getattr(parsed_args, "search_regex")
    repositories_to_search = getattr(parsed_args, "repositories")
    organization = getattr(parsed_args, "organization")

    stats = {}
    if organization:
        repos = list_github_repositories(organization=organization, auth=(user, password))
        repo_owner = organization
    else:
        repos = list_github_repositories(username=user, auth=(user, password))
        repo_owner = user

    git_repo = None

    for repo in repos:
        # skip the repos that we don't want to search
        if repositories_to_search and repo["name"] not in repositories_to_search:
            continue
        # go through each commit find what we are looking for
        git_repo = GitHubVanityAnalytics(repo_owner, repo["name"], user, password)

        # find each file that we care about
        found_files = git_repo.search_for_file(
            regex=regex, path="", recursive=True, file_type="file")
        for file_found in found_files:
            commits = git_repo.get_commits(
                path=file_found['path'],
                since=datetime.datetime(2015, 1, 1).isoformat(),
                until=datetime.datetime(2015, 5, 1).isoformat()
            )

            for commit in commits:
                stats = git_repo.get_commit_stats(
                    commit["sha"], stats, path=file_found['path'])
    
    pprint.pprint(stats)

    if git_repo:
        pprint.pprint(git_repo.get_rate_limits())
    


if __name__ == "__main__":
    main()
