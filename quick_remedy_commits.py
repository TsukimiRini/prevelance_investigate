# coding=utf-8
import os
from git.repo import Repo
import json
from sys import platform

if platform == "darwin":
    work_dir = "/Users/tannpopo/Documents/Study/ChangeLint/repo"
    stats_dir = "."
else:
    work_dir = "/home/repos"
    stats_dir = "/home/yuailun/quick_remedy_commits"


def getQRCommits(repo_name):
    commits_list = []
    shas = set()
    repo = Repo(os.path.join(work_dir, repo_name))
    
    for b in repo.remote().fetch():
        if '/' not in b.name:
            continue
        print("start to check branch {} of {}".format(b.name, repo_name))
        branch_name = b.name.split('/')[1]
        repo.git.checkout('-B', branch_name, b.name)
        commits = list(repo.iter_commits(branch_name))

        for idx, commit in enumerate(commits):
            if str(commit) in shas:
                break
            else:
                shas.add(str(commit))
            commit_collection = {}
            xml_cnt = 0
            kot_jav_cnt = 0

            file_list = list(commit.stats.files)
            for file in file_list:
                if len(file) > 4 and file[-4:] == '.xml':
                    xml_cnt += 1
                elif len(file) > 3 and file[-3:] == '.kt' or len(
                        file) > 5 and file[-5:] == '.java':
                    kot_jav_cnt += 1
            if xml_cnt >= 1 and kot_jav_cnt >= 1:
                if idx != 0:
                    time_next_commit = commits[
                        idx - 1].committed_datetime - commit.committed_datetime
                    if time_next_commit.total_seconds() / 60 <= 30 and len(
                            commit.parents) < 2:
                        commit_collection["commit_id"] = str(commit)
                        commit_collection["commit_msg"] = str.strip(commit.message)
                        commit_collection["commit_time"] = str(
                            commit.committed_datetime)
                        commit_collection["remedy_id"] = str(commits[idx - 1])
                        commit_collection["remedy_time"] = str(
                            commits[idx - 1].committed_datetime)
                        commit_collection["remedy_msg"] = str.strip(
                            commits[idx - 1].message)
                        commits_list.append(commit_collection)

            # diff_files = []
            # if not commit.parents:
            #     continue
            # else:
            #     for diff in commit.diff(commit.parents[0]):
            #         diff_file = {}
            #         diff_file["file_path"] = diff.a_path
            #         diff_file["change_type"] = diff.change_type
            #         diff_file["lang"] = os.path.splitext(diff.a_path)[1][1:]
            #         diff_files.append(diff_file)

            # commit_collection["diff_files"] = diff_files
            # commit_collection["parent_commit_num"] = len(commit.parents)

    repo_dump = json.dumps(commits_list, indent=2, ensure_ascii=False)
    with open(os.path.join(stats_dir, repo_name), "w") as commit_fd:
        commit_fd.write(repo_dump)
        print(repo_name + " done")


def allRepos():
    repo_list = "/home/yuailun/repo_list"
    with open(repo_list) as list_fd:
        json_obj = json.load(list_fd)
        assert (len(json_obj) == 100)
        for repo in json_obj:
            assert (os.path.exists(
                os.path.join(work_dir,
                             repo["owner"]["login"] + "-" + repo["name"])))
            getQRCommits(repo["owner"]["login"] + "-" + repo["name"])


if platform == "linux":
    allRepos()
elif platform == "darwin":
    getQRCommits("TeamNewPipe-NewPipe")