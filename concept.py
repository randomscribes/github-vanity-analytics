'''
Testing script
'''
import pprint
import requests


GIT_HUB_HOST = "https://api.github.com"

# get repository

# get past 30 days of commits on repository
def get_commits(owner, repo, **kwargs):
    """
    Get commits made to a repository.
    :param owner: <string>
    :param repo: <string>
    :param kwargs: <string> Arguments to be passed to the api call
        See https://developer.github.com/v3/repos/commits/#list-commits-on-a-repository
    :return: <dict> results   
    """
    url = "{host}/repos/{owner}/{repo}/commits".format(host=GIT_HUB_HOST, owner=owner, repo=repo)
    response = requests.get(url, params=kwargs)
    return response.json()
	

# go through each commit, find those that are from test and count the number of change

pprint.pprint(get_commits("randomscribes", "Doc-To-HTML"))

