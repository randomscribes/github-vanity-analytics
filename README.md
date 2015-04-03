# github-vanity-analytics
A simple python library for retrieving GitHub Analytics.


## Script Options

* `-u`, `--user` <string> *required* - GitHub User, used for API quota & the repo owner (if organizaiton is not specified).
* `-p`, `--password` <string> *required* - Used to authenticate your GitHub account.
* `-s`, `--search_regex` <string> *required* - What files to search github for.
* `-r`, `--repositories` <list> - Which reposities to search for files. If no reposities are give, will look through all reposities.
* `-o`, `--organization` <string> - The organization where the repositories are located.
* `--start_path` <string> - The project path to start looking for files.
