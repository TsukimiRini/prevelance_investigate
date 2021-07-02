import os
import json
from git import Repo
import sys

szz_dir = sys.argv[1]
repo_dir = sys.argv[2]
list_path = sys.argv[3]

all_commit_cnt = 0
commit_cross = 0


def forOneRepo(owner, repo_name):
    global all_commit_cnt
    global commit_cross

    repo_cross_commit_cnt = 0
    repo_commit_cnt = 0
    repo = Repo(os.path.join(repo_dir, owner + "-" + repo_name))
    pairs = set()
    with open(
            os.path.join(szz_dir, repo_name, "results",
                         "fix_and_introducers_pairs.json"), 'r') as fd:
        content = fd.read()
        array = json.loads(content)
        for pair in array:
            fix_commit = pair[0]
            bug_commit = pair[1]
            p = (fix_commit, bug_commit)
            if p in pairs:
                continue
            else:
                pairs.add(p)
            commit = repo.commit(bug_commit)

            xml_cnt = 0
            kot_jav_cnt = 0
            all_commit_cnt += 1
            repo_commit_cnt += 1

            # if idx == len(commits)-1:
            file_list = list(commit.stats.files)
            for file in file_list:
                if len(file) > 4 and file[-4:] == '.xml':
                    xml_cnt += 1
                elif len(file) > 3 and file[-3:] == '.kt' or len(
                        file) > 5 and file[-5:] == '.java':
                    kot_jav_cnt += 1
            if xml_cnt >= 1 and kot_jav_cnt >= 1:
                repo_cross_commit_cnt += 1
                commit_cross += 1
    if repo_commit_cnt == 0:
        print("{}/{} has no bug-intro commits".format(owner, repo_name))
    else:
        print(
            "{}/{} bug-intro cross-lang commits: {}, all bug-intro: {}, percent: {}"
            .format(owner, repo_name, repo_cross_commit_cnt, repo_commit_cnt,
                    float(repo_cross_commit_cnt) / repo_commit_cnt))


def all():
    lines = []
    with open(list_path, "r") as fd:
        lines = [str.strip(line) for line in fd.readlines()]
    for line in lines:
        owner, filename = line.split(" ")
        forOneRepo(owner, filename)
    print(16 * '=')
    print("cross-lang: {}, all: {}".format(commit_cross, all_commit_cnt))


all()