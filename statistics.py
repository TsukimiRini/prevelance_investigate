import os
from git.repo import Repo
import json

# work_dir = "/Users/tannpopo/Documents/Study/ChangeLint/repos"
# work_dir = "/Users/tannpopo/Projects"
work_dir = "/home/repos"


def check(repo_name):
    print("="*8, "start to check repo ", repo_name, "="*8)
    commit_total = 0
    commit_cross = 0
    percent = 0

    repo = Repo(os.path.join(work_dir, repo_name))
    commits = list(repo.iter_commits())
    commit_total = len(commits)
    for idx, commit in enumerate(commits):
        xml_cnt = 0
        kot_jav_cnt = 0

        # if idx == len(commits)-1:
        for file in list(commit.stats.files):
            if len(file) > 4 and file[-4:] == '.xml':
                xml_cnt += 1
            elif len(file) > 3 and file[-3:] == '.kt' or len(file) > 5 and file[-5:] == '.java':
                kot_jav_cnt += 1
        if xml_cnt >= 1 and kot_jav_cnt >= 1:
            commit_cross += 1
        #     break
        # diff_index = commit.diff(commits[idx+1])

        # for diff_item in diff_index:
        #     if diff_item.a_path[-4:] == '.xml':
        #         xml_cnt += 1
        #     elif diff_item.a_path[-3:] == '.kt' or diff_item.a_path[-5:] == '.java':
        #         kot_jav_cnt += 1
        # if xml_cnt >= 1 and kot_jav_cnt >= 1:
        #     commit_cross += 1

    percent = float(commit_cross)/commit_total
    res = "Total: {}, Cross: {}, Percent: {}".format(commit_total, commit_cross, percent)
    print(res)
    print("="*8, "check repo ", repo_name, "completed", "="*8)
    return commit_total, commit_cross, percent


def allRepos():
    json_file = "/home/yuailun/android-java-repo"
    with open(os.path.join(work_dir, json_file)) as json_fd:
        load_dict = json.load(json_fd)
        for idx, item in enumerate(load_dict["items"]):
            if idx >= cnt:
                return
            clone_url = item["clone_url"]
            name = item["name"]
            Repo.clone_from(clone_url, to_path=os.path.join(download_path, name), progress=Progress())