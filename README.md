# Survey: Prevalence of multi-language commits in Android-based software development for top 100 Android applications
## clone.py
### requirement
- json file generated from Github Rest API containing all the applications in sort of stars which is filtered by language
### function
- clone all the applications according to the requirement (app directory in repo root)
- generate a json file containing applications cloned
## statistics.py
### requirement
- cloned repos
- repo list
### function
- collect multi-lang commits of cloned repos
- calculate the percentage of multi-lang commits in each repo/all repo
## bag_of_words.py
### requirement
- cloned repos
- repo list
### function
- collect words in commit messages of multi-lang commits and sort them by frequecy
# Collect all multi-lang commits in Android applications
## get_commits.py
### requirement
- cloned repos
- repo list
### function
- generate a json file of multi-lang commits for each repo
# Calculate the percentage of multi-lang commits in bug-introducing repos
## get_events.py
### requirement
- cloned repos
- repo list
- github token
### function
- generate a json file of issues with commits for each repo
- save a list of all the repos with valid issues
## szz_traverse.py
### requirement
- issue list of repos
- jar file of szz algorithm
### function
- apply szz file to each repo issues
- generate a json file of bug-introducing commits for each repo
## stat_szz_res.py
### requirement
- list of repos with valid issues
- cloned repos
- json files of bug-introducing commits
### function
- count multi-lang commits in bug-introducing commits
